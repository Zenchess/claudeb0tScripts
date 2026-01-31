const std = @import("std");

fn findHackmudPid(allocator: std.mem.Allocator) !?u32 {
    // Try reading from scanner.pid file first
    const pid_file_path = "/home/jacob/hackmud/scanner.pid";
    if (std.fs.cwd().readFileAlloc(allocator, pid_file_path, 1024)) |contents| {
        defer allocator.free(contents);
        const trimmed = std.mem.trim(u8, contents, &std.ascii.whitespace);
        if (std.fmt.parseInt(u32, trimmed, 10)) |pid| {
            // Verify process exists
            const mem_path = try std.fmt.allocPrint(allocator, "/proc/{d}/mem", .{pid});
            defer allocator.free(mem_path);

            std.fs.accessAbsolute(mem_path, .{}) catch {
                return null;
            };
            return pid;
        } else |_| {}
    } else |_| {}

    // Fallback: use pgrep
    var child = std.process.Child.init(&[_][]const u8{ "pgrep", "hackmud" }, allocator);
    child.stdout_behavior = .Pipe;
    try child.spawn();

    const stdout = child.stdout orelse return null;
    defer stdout.close();

    var buf: [128]u8 = undefined;
    const bytes_read = try stdout.readAll(&buf);

    _ = try child.wait();

    if (bytes_read > 0) {
        const trimmed = std.mem.trim(u8, buf[0..bytes_read], &std.ascii.whitespace);
        if (std.fmt.parseInt(u32, trimmed, 10)) |pid| {
            return pid;
        } else |_| {}
    }

    return null;
}

const Address = struct {
    addr: usize,
    size: usize,
};

fn getHeapAddresses(allocator: std.mem.Allocator, pid: u32) ![]Address {
    const maps_path = try std.fmt.allocPrint(allocator, "/proc/{d}/maps", .{pid});
    defer allocator.free(maps_path);

    const contents = try std.fs.cwd().readFileAlloc(allocator, maps_path, 1024 * 1024);
    defer allocator.free(contents);

    var addresses: std.ArrayList(Address) = .init(allocator);
    errdefer addresses.deinit();

    var lines = std.mem.splitScalar(u8, contents, '\n');
    while (lines.next()) |line| {
        if (std.mem.indexOf(u8, line, "[heap]")) |_| {
            var parts = std.mem.splitScalar(u8, line, ' ');
            if (parts.next()) |addr_range| {
                if (std.mem.indexOf(u8, addr_range, "-")) |dash_pos| {
                    const start_str = addr_range[0..dash_pos];
                    const end_str = addr_range[dash_pos + 1 ..];

                    const start = try std.fmt.parseInt(usize, start_str, 16);
                    const end = try std.fmt.parseInt(usize, end_str, 16);

                    const region_size = end - start;
                    if (region_size > 0) {
                        var i: usize = 0;
                        while (i < 100) : (i += 1) {
                            const offset = (region_size / 100) * i;
                            try addresses.append(.{ .addr = start + offset, .size = 8 });
                        }
                    }
                }
            }
            break;
        }
    }

    return addresses.toOwnedSlice();
}

fn benchmarkMemoryReads(allocator: std.mem.Allocator, pid: u32, addresses: []const Address) !struct { successful: usize, elapsed_micros: u64 } {
    const mem_path = try std.fmt.allocPrint(allocator, "/proc/{d}/mem", .{pid});
    defer allocator.free(mem_path);

    const mem_file = try std.fs.openFileAbsolute(mem_path, .{});
    defer mem_file.close();

    const timer = try std.time.Timer.start();

    var successful: usize = 0;
    var buffer: [8]u8 = undefined;

    for (addresses) |addr_info| {
        mem_file.seekTo(addr_info.addr) catch continue;
        const bytes_read = mem_file.read(buffer[0..addr_info.size]) catch continue;
        if (bytes_read == addr_info.size) {
            successful += 1;
        }
    }

    const elapsed_nanos = timer.read();
    const elapsed_micros = elapsed_nanos / 1000;

    return .{
        .successful = successful,
        .elapsed_micros = elapsed_micros,
    };
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    // Use debug print as stdout API changed in Zig 0.15
    const print = std.debug.print;

    print("=== Zig Memory Reading Benchmark ===\n\n", .{});

    // Find hackmud PID
    const pid = try findHackmudPid(allocator) orelse {
        print("Error: hackmud process not found\n", .{});
        print("Make sure hackmud is running\n", .{});
        return;
    };

    print("Found hackmud process: PID {d}\n", .{pid});

    // Get heap addresses
    print("Finding heap addresses...\n", .{});
    const addresses = try getHeapAddresses(allocator, pid);
    defer allocator.free(addresses);

    if (addresses.len == 0) {
        print("Error: No heap addresses found\n", .{});
        return;
    }

    print("Found {d} addresses to test\n\n", .{addresses.len});

    // Run benchmark
    print("Running benchmark (reading {d} locations)...\n", .{addresses.len});
    const result = try benchmarkMemoryReads(allocator, pid, addresses);

    print("\nResults:\n", .{});
    print("  Successful reads: {d}/{d}\n", .{ result.successful, addresses.len });
    print("  Total time:       {d:.3} ms\n", .{@as(f64, @floatFromInt(result.elapsed_micros)) / 1000.0});
    print("  Time per read:    {d:.3} µs\n", .{@as(f64, @floatFromInt(result.elapsed_micros)) / @as(f64, @floatFromInt(addresses.len))});

    // Run multiple iterations for average
    print("\n Running 10 iterations for average...\n", .{});
    var times: std.ArrayList(u64) = .init(allocator);
    defer times.deinit();

    var i: usize = 0;
    while (i < 10) : (i += 1) {
        const iter_result = try benchmarkMemoryReads(allocator, pid, addresses);
        try times.append(iter_result.elapsed_micros);
    }

    var total: u64 = 0;
    var min: u64 = std.math.maxInt(u64);
    var max: u64 = 0;

    for (times.items) |time| {
        total += time;
        if (time < min) min = time;
        if (time > max) max = time;
    }

    const avg = total / times.items.len;

    print("  Average: {d:.3} ms\n", .{@as(f64, @floatFromInt(avg)) / 1000.0});
    print("  Min:     {d:.3} ms\n", .{@as(f64, @floatFromInt(min)) / 1000.0});
    print("  Max:     {d:.3} ms\n", .{@as(f64, @floatFromInt(max)) / 1000.0});
    print("  Per read: {d:.3} µs\n", .{@as(f64, @floatFromInt(avg)) / @as(f64, @floatFromInt(addresses.len))});
}
