use sha2::{Sha256, Digest};
use md5::Md5;
use std::fs::File;
use std::io::{self, Read};
use std::time::Instant;
use std::path::{Path, PathBuf};
use std::env;

fn compute_hash_sha256(file_path: &Path) -> io::Result<(String, u64, u128)> {
    let start = Instant::now();

    let mut file = File::open(file_path)?;
    let mut hasher = Sha256::new();
    let mut buffer = [0u8; 8192];
    let mut total_bytes = 0u64;

    loop {
        let bytes_read = file.read(&mut buffer)?;
        if bytes_read == 0 {
            break;
        }
        hasher.update(&buffer[..bytes_read]);
        total_bytes += bytes_read as u64;
    }

    let hash = hasher.finalize();
    let hash_hex = format!("{:x}", hash);
    let elapsed_micros = start.elapsed().as_micros();

    Ok((hash_hex, total_bytes, elapsed_micros))
}

fn compute_hash_md5(file_path: &Path) -> io::Result<(String, u64, u128)> {
    let start = Instant::now();

    let mut file = File::open(file_path)?;
    let mut hasher = Md5::new();
    let mut buffer = [0u8; 8192];
    let mut total_bytes = 0u64;

    loop {
        let bytes_read = file.read(&mut buffer)?;
        if bytes_read == 0 {
            break;
        }
        hasher.update(&buffer[..bytes_read]);
        total_bytes += bytes_read as u64;
    }

    let hash = hasher.finalize();
    let hash_hex = format!("{:x}", hash);
    let elapsed_micros = start.elapsed().as_micros();

    Ok((hash_hex, total_bytes, elapsed_micros))
}

fn get_default_paths() -> (PathBuf, PathBuf) {
    let home = env::var("HOME").expect("HOME not set");
    let game_path = PathBuf::from(home)
        .join(".local/share/Steam/steamapps/common/hackmud");

    let core_dll = game_path.join("hackmud_lin_Data/Managed/Core.dll");
    let level0 = game_path.join("hackmud_lin_Data/level0");

    (core_dll, level0)
}

fn format_size(bytes: u64) -> String {
    if bytes < 1024 {
        format!("{} bytes", bytes)
    } else if bytes < 1024 * 1024 {
        format!("{:.2} KB", bytes as f64 / 1024.0)
    } else {
        format!("{:.2} MB", bytes as f64 / (1024.0 * 1024.0))
    }
}

fn main() {
    println!("=== Rust Hash Performance Test: SHA256 vs MD5 ===\n");

    let (core_dll_path, level0_path) = if env::args().len() >= 3 {
        let mut args = env::args().skip(1);
        (
            PathBuf::from(args.next().unwrap()),
            PathBuf::from(args.next().unwrap())
        )
    } else {
        println!("Using default paths...\n");
        get_default_paths()
    };

    // Test Core.dll
    println!("Hashing Core.dll: {}", core_dll_path.display());

    // SHA256
    match compute_hash_sha256(&core_dll_path) {
        Ok((hash, size, micros)) => {
            println!("  SHA256 Hash: {}", hash);
            println!("  Size:        {}", format_size(size));
            println!("  Time:        {:.3} ms ({} µs)", micros as f64 / 1000.0, micros);
        }
        Err(e) => {
            eprintln!("  SHA256 Error: {}", e);
        }
    }

    // MD5
    match compute_hash_md5(&core_dll_path) {
        Ok((hash, _, micros)) => {
            println!("  MD5 Hash:    {}", hash);
            println!("  Time:        {:.3} ms ({} µs)", micros as f64 / 1000.0, micros);
        }
        Err(e) => {
            eprintln!("  MD5 Error:   {}", e);
        }
    }

    println!();

    // Test level0
    println!("Hashing level0: {}", level0_path.display());

    // SHA256
    match compute_hash_sha256(&level0_path) {
        Ok((hash, size, micros)) => {
            println!("  SHA256 Hash: {}", hash);
            println!("  Size:        {}", format_size(size));
            println!("  Time:        {:.3} ms ({} µs)", micros as f64 / 1000.0, micros);
        }
        Err(e) => {
            eprintln!("  SHA256 Error: {}", e);
        }
    }

    // MD5
    match compute_hash_md5(&level0_path) {
        Ok((hash, _, micros)) => {
            println!("  MD5 Hash:    {}", hash);
            println!("  Time:        {:.3} ms ({} µs)", micros as f64 / 1000.0, micros);
        }
        Err(e) => {
            eprintln!("  MD5 Error:   {}", e);
        }
    }

    println!();

    // Combined performance test (10 iterations)
    println!("Performance comparison (10 iterations each):");

    let mut sha256_times = Vec::new();
    let mut md5_times = Vec::new();

    for _ in 0..10 {
        // SHA256
        let start = Instant::now();
        let _ = compute_hash_sha256(&core_dll_path);
        let _ = compute_hash_sha256(&level0_path);
        sha256_times.push(start.elapsed().as_micros());

        // MD5
        let start = Instant::now();
        let _ = compute_hash_md5(&core_dll_path);
        let _ = compute_hash_md5(&level0_path);
        md5_times.push(start.elapsed().as_micros());
    }

    let sha256_avg = sha256_times.iter().sum::<u128>() / sha256_times.len() as u128;
    let md5_avg = md5_times.iter().sum::<u128>() / md5_times.len() as u128;

    println!("  SHA256 avg: {:.3} ms", sha256_avg as f64 / 1000.0);
    println!("  MD5 avg:    {:.3} ms", md5_avg as f64 / 1000.0);
    println!("  Speedup:    {:.2}x faster with MD5", sha256_avg as f64 / md5_avg as f64);
}
