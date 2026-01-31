const std = @import("std");

const Address = struct {
    addr: usize,
    size: usize,
};

fn findHackmudPid() !u32 {
    const pid_file = try std.fs.cwd().openFile("/home/jacob/hackmud/scanner.pid", .{});
    defer pid_file.close();

    var buf: [32]u8 = undefined;
    const bytes_read = try pid_file.readAll(&buf);
    const pid_str = std.mem.trim(u8, buf[0..bytes_read], &std.ascii.whitespace);
    return try std.fmt.parseInt(u32, pid_str, 10);
}

fn getHeapAddresses(pid: u32, addresses: *[100]Address) !usize {
    var buf: [32]u8 = undefined;
    const maps_path = try std.fmt.bufPrint(&buf, "/proc/{d}/maps", .{pid});

    const maps_file = try std.fs.openFileAbsolute(maps_path, .{});
    defer maps_file.close();

    const contents = try maps_file.readToEndAlloc(std.heap.page_allocator, 1024 * 1024);
    defer std.heap.page_allocator.free(contents);

    var lines = std.mem.splitScalar(u8, contents, '\n');
    var count: usize = 0;

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
                            addresses[count] = .{ .addr = start + offset, .size = 8 };
                            count += 1;
                        }
                    }
                }
            }
            break;
        }
    }

    return count;
}

fn benchmarkMemoryReads(pid: u32, addresses: []const Address) !struct { successful: usize, elapsed_micros: u64 } {
    var buf: [32]u8 = undefined;
    const mem_path = try std.fmt.bufPrint(&buf, "/proc/{d}/mem", .{pid});

    const mem_file = try std.fs.openFileAbsolute(mem_path, .{});
    defer mem_file.close();

    var timer = try std.time.Timer.start();

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
    const print = std.debug.print;

    print("=== Zig Memory Reading Benchmark ===\n\n", .{});

    // Find hackmud PID
    const pid = findHackmudPid() catch {
        print("Error: hackmud process not found\n", .{});
        return;
    };

    print("Found hackmud process: PID {d}\n", .{pid});

    // Get heap addresses
    print("Finding heap addresses...\n", .{});
    var addresses: [100]Address = undefined;
    const count = try getHeapAddresses(pid, &addresses);

    if (count == 0) {
        print("Error: No heap addresses found\n", .{});
        return;
    }

    print("Found {d} addresses to test\n\n", .{count});

    // Run benchmark
    print("Running benchmark (reading {d} locations)...\n", .{count});
    const result = try benchmarkMemoryReads(pid, addresses[0..count]);

    print("\nResults:\n", .{});
    print("  Successful reads: {d}/{d}\n", .{ result.successful, count });
    print("  Total time:       {d:.3} ms\n", .{@as(f64, @floatFromInt(result.elapsed_micros)) / 1000.0});
    print("  Time per read:    {d:.3} µs\n", .{@as(f64, @floatFromInt(result.elapsed_micros)) / @as(f64, @floatFromInt(count))});

    // Run multiple iterations for average
    print("\n Running 10 iterations for average...\n", .{});
    var times: [10]u64 = undefined;

    var i: usize = 0;
    while (i < 10) : (i += 1) {
        const iter_result = try benchmarkMemoryReads(pid, addresses[0..count]);
        times[i] = iter_result.elapsed_micros;
    }

    var total: u64 = 0;
    var min: u64 = std.math.maxInt(u64);
    var max: u64 = 0;

    for (times) |time| {
        total += time;
        if (time < min) min = time;
        if (time > max) max = time;
    }

    const avg = total / times.len;

    print("  Average: {d:.3} ms\n", .{@as(f64, @floatFromInt(avg)) / 1000.0});
    print("  Min:     {d:.3} ms\n", .{@as(f64, @floatFromInt(min)) / 1000.0});
    print("  Max:     {d:.3} ms\n", .{@as(f64, @floatFromInt(max)) / 1000.0});
    print("  Per read: {d:.3} µs\n", .{@as(f64, @floatFromInt(avg)) / @as(f64, @floatFromInt(count))});
}
