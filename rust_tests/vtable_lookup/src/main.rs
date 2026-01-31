use std::fs::File;
use std::io::{Read, Seek, SeekFrom};
use std::time::Instant;
use std::path::Path;

fn find_hackmud_pid() -> Option<u32> {
    // Try reading from scanner.pid file first
    if let Ok(pid_str) = std::fs::read_to_string("/home/jacob/hackmud/scanner.pid") {
        if let Ok(pid) = pid_str.trim().parse::<u32>() {
            // Verify process exists
            if Path::new(&format!("/proc/{}/mem", pid)).exists() {
                return Some(pid);
            }
        }
    }

    // Fallback: search for hackmud process
    if let Ok(output) = std::process::Command::new("pgrep")
        .arg("hackmud")
        .output()
    {
        if output.status.success() {
            let pid_str = String::from_utf8_lossy(&output.stdout);
            if let Ok(pid) = pid_str.trim().parse::<u32>() {
                return Some(pid);
            }
        }
    }

    None
}

fn read_memory_at(mem_file: &mut File, address: usize, size: usize) -> std::io::Result<Vec<u8>> {
    mem_file.seek(SeekFrom::Start(address as u64))?;
    let mut buffer = vec![0u8; size];
    mem_file.read_exact(&mut buffer)?;
    Ok(buffer)
}

fn benchmark_memory_reads(pid: u32, addresses: &[(usize, usize)]) -> (usize, u128) {
    let mem_path = format!("/proc/{}/mem", pid);
    let mut mem_file = match File::open(&mem_path) {
        Ok(f) => f,
        Err(e) => {
            eprintln!("Failed to open {}: {}", mem_path, e);
            return (0, 0);
        }
    };

    let start = Instant::now();
    let mut total_bytes = 0;
    let mut successful_reads = 0;

    for &(addr, size) in addresses {
        if let Ok(data) = read_memory_at(&mut mem_file, addr, size) {
            total_bytes += data.len();
            successful_reads += 1;
        }
    }

    let elapsed_micros = start.elapsed().as_micros();
    (successful_reads, elapsed_micros)
}

fn get_heap_addresses(pid: u32) -> Vec<(usize, usize)> {
    let maps_path = format!("/proc/{}/maps", pid);
    let maps_content = match std::fs::read_to_string(&maps_path) {
        Ok(c) => c,
        Err(_) => return Vec::new(),
    };

    let mut addresses = Vec::new();

    // Find heap regions and collect some addresses
    for line in maps_content.lines() {
        if line.contains("[heap]") {
            let parts: Vec<&str> = line.split_whitespace().collect();
            if let Some(addr_range) = parts.get(0) {
                if let Some((start_str, end_str)) = addr_range.split_once('-') {
                    if let (Ok(start), Ok(end)) = (
                        usize::from_str_radix(start_str, 16),
                        usize::from_str_radix(end_str, 16),
                    ) {
                        // Sample 100 addresses from the heap region
                        let region_size = end - start;
                        if region_size > 0 {
                            for i in 0..100 {
                                let offset = (region_size / 100) * i;
                                addresses.push((start + offset, 8)); // Read 8 bytes at each location
                            }
                        }
                    }
                }
            }
        }
    }

    addresses
}

fn main() {
    println!("=== Rust Memory Reading Benchmark ===\n");

    // Find hackmud PID
    let pid = match find_hackmud_pid() {
        Some(p) => {
            println!("Found hackmud process: PID {}", p);
            p
        }
        None => {
            eprintln!("Error: hackmud process not found");
            eprintln!("Make sure hackmud is running");
            return;
        }
    };

    // Get some addresses from heap to read
    println!("Finding heap addresses...");
    let addresses = get_heap_addresses(pid);

    if addresses.is_empty() {
        eprintln!("Error: No heap addresses found");
        return;
    }

    println!("Found {} addresses to test\n", addresses.len());

    // Run benchmark
    println!("Running benchmark (reading {} locations)...", addresses.len());
    let (successful, elapsed_micros) = benchmark_memory_reads(pid, &addresses);

    println!("\nResults:");
    println!("  Successful reads: {}/{}", successful, addresses.len());
    println!("  Total time:       {:.3} ms", elapsed_micros as f64 / 1000.0);
    println!("  Time per read:    {:.3} µs", elapsed_micros as f64 / addresses.len() as f64);

    // Run multiple iterations for average
    println!("\n Running 10 iterations for average...");
    let mut times = Vec::new();

    for _ in 0..10 {
        let (_, elapsed) = benchmark_memory_reads(pid, &addresses);
        times.push(elapsed);
    }

    let avg = times.iter().sum::<u128>() / times.len() as u128;
    let min = times.iter().min().unwrap();
    let max = times.iter().max().unwrap();

    println!("  Average: {:.3} ms", avg as f64 / 1000.0);
    println!("  Min:     {:.3} ms", *min as f64 / 1000.0);
    println!("  Max:     {:.3} ms", *max as f64 / 1000.0);
    println!("  Per read: {:.3} µs", avg as f64 / addresses.len() as f64);
}
