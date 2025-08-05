#!/bin/bash

# ByteBill ISP Speed Test Script
# This script runs speed tests on both WAN interfaces and logs the results

# Configuration
WAN1_INTERFACE="enx1"
WAN2_INTERFACE="enx2"
LOG_FILE="/var/log/bytebill-speedtest.log"
RESULT_FILE="/var/lib/bytebill/speedtest_results.json"

# Ensure directories exist
mkdir -p /var/lib/bytebill
mkdir -p /var/log

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Function to check if interface is up and has IP
check_interface() {
    local interface=$1
    
    # Check if interface exists and is up
    if ! ip link show "$interface" >/dev/null 2>&1; then
        echo "Interface $interface does not exist"
        return 1
    fi
    
    if ! ip link show "$interface" | grep -q "state UP"; then
        echo "Interface $interface is down"
        return 1
    fi
    
    # Check if interface has IP address
    if ! ip addr show "$interface" | grep -q "inet "; then
        echo "Interface $interface has no IP address"
        return 1
    fi
    
    echo "Interface $interface is ready"
    return 0
}

# Function to run speedtest on specific interface
run_speedtest() {
    local interface=$1
    local interface_name=$2
    
    log_message "Running speed test on $interface_name ($interface)..."
    
    # Check if speedtest-cli is installed
    if ! command -v speedtest-cli >/dev/null 2>&1; then
        log_message "ERROR: speedtest-cli is not installed. Install with: pip install speedtest-cli"
        return 1
    fi
    
    # Check interface status
    if ! check_interface "$interface"; then
        log_message "ERROR: $interface_name ($interface) is not ready for testing"
        return 1
    fi
    
    # Run speedtest with interface binding
    local temp_file=$(mktemp)
    
    # Try to bind to interface
    if speedtest-cli --interface "$interface" --simple --timeout 60 > "$temp_file" 2>&1; then
        local ping_ms=$(grep "Ping:" "$temp_file" | awk '{print $2}')
        local download_mbps=$(grep "Download:" "$temp_file" | awk '{print $2}')
        local upload_mbps=$(grep "Upload:" "$temp_file" | awk '{print $2}')
        
        # Create JSON result
        local timestamp=$(date -Iseconds)
        local result=$(cat <<EOF
{
  "timestamp": "$timestamp",
  "interface": "$interface",
  "interface_name": "$interface_name",
  "ping_ms": $ping_ms,
  "download_mbps": $download_mbps,
  "upload_mbps": $upload_mbps,
  "status": "success"
}
EOF
)
        
        log_message "$interface_name Results: Ping: ${ping_ms}ms, Download: ${download_mbps} Mbps, Upload: ${upload_mbps} Mbps"
        echo "$result"
        
    else
        log_message "ERROR: Speed test failed for $interface_name ($interface)"
        log_message "Error output: $(cat "$temp_file")"
        
        local timestamp=$(date -Iseconds)
        local result=$(cat <<EOF
{
  "timestamp": "$timestamp",
  "interface": "$interface",
  "interface_name": "$interface_name",
  "ping_ms": null,
  "download_mbps": null,
  "upload_mbps": null,
  "status": "failed",
  "error": "$(cat "$temp_file" | tr '\n' ' ' | sed 's/"/\\"/g')"
}
EOF
)
        echo "$result"
    fi
    
    rm -f "$temp_file"
}

# Function to save results to JSON file
save_results() {
    local wan1_result="$1"
    local wan2_result="$2"
    
    local combined_result=$(cat <<EOF
{
  "test_time": "$(date -Iseconds)",
  "wan1": $wan1_result,
  "wan2": $wan2_result
}
EOF
)
    
    # Save to file
    echo "$combined_result" > "$RESULT_FILE"
    
    # Also append to history file
    local history_file="/var/lib/bytebill/speedtest_history.jsonl"
    echo "$combined_result" >> "$history_file"
    
    # Keep only last 100 entries in history
    if [ -f "$history_file" ]; then
        tail -n 100 "$history_file" > "${history_file}.tmp"
        mv "${history_file}.tmp" "$history_file"
    fi
}

# Function to run connectivity test
test_connectivity() {
    local interface=$1
    local test_host="8.8.8.8"
    
    if ping -c 3 -W 5 -I "$interface" "$test_host" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Main execution
main() {
    log_message "Starting ByteBill ISP speed test..."
    
    # Test connectivity first
    log_message "Testing basic connectivity..."
    
    wan1_connectivity="false"
    wan2_connectivity="false"
    
    if test_connectivity "$WAN1_INTERFACE"; then
        wan1_connectivity="true"
        log_message "WAN1 ($WAN1_INTERFACE) connectivity: OK"
    else
        log_message "WAN1 ($WAN1_INTERFACE) connectivity: FAILED"
    fi
    
    if test_connectivity "$WAN2_INTERFACE"; then
        wan2_connectivity="true"
        log_message "WAN2 ($WAN2_INTERFACE) connectivity: OK"
    else
        log_message "WAN2 ($WAN2_INTERFACE) connectivity: FAILED"
    fi
    
    # Run speed tests
    local wan1_result
    local wan2_result
    
    if [ "$wan1_connectivity" = "true" ]; then
        wan1_result=$(run_speedtest "$WAN1_INTERFACE" "WAN1")
    else
        local timestamp=$(date -Iseconds)
        wan1_result=$(cat <<EOF
{
  "timestamp": "$timestamp",
  "interface": "$WAN1_INTERFACE",
  "interface_name": "WAN1",
  "ping_ms": null,
  "download_mbps": null,
  "upload_mbps": null,
  "status": "no_connectivity"
}
EOF
)
    fi
    
    if [ "$wan2_connectivity" = "true" ]; then
        wan2_result=$(run_speedtest "$WAN2_INTERFACE" "WAN2")
    else
        local timestamp=$(date -Iseconds)
        wan2_result=$(cat <<EOF
{
  "timestamp": "$timestamp",
  "interface": "$WAN2_INTERFACE",
  "interface_name": "WAN2",
  "ping_ms": null,
  "download_mbps": null,
  "upload_mbps": null,
  "status": "no_connectivity"
}
EOF
)
    fi
    
    # Save results
    save_results "$wan1_result" "$wan2_result"
    
    log_message "Speed test completed. Results saved to $RESULT_FILE"
    
    # Display summary
    echo "=== Speed Test Summary ==="
    echo "WAN1 ($WAN1_INTERFACE): $(echo "$wan1_result" | jq -r '.status')"
    if echo "$wan1_result" | jq -e '.download_mbps' >/dev/null 2>&1; then
        echo "  Download: $(echo "$wan1_result" | jq -r '.download_mbps') Mbps"
        echo "  Upload: $(echo "$wan1_result" | jq -r '.upload_mbps') Mbps"
        echo "  Ping: $(echo "$wan1_result" | jq -r '.ping_ms') ms"
    fi
    
    echo "WAN2 ($WAN2_INTERFACE): $(echo "$wan2_result" | jq -r '.status')"
    if echo "$wan2_result" | jq -e '.download_mbps' >/dev/null 2>&1; then
        echo "  Download: $(echo "$wan2_result" | jq -r '.download_mbps') Mbps"
        echo "  Upload: $(echo "$wan2_result" | jq -r '.upload_mbps') Mbps"
        echo "  Ping: $(echo "$wan2_result" | jq -r '.ping_ms') ms"
    fi
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "This script should be run as root for proper interface access"
    exit 1
fi

# Check for required tools
missing_tools=""
for tool in speedtest-cli jq ping ip; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        missing_tools="$missing_tools $tool"
    fi
done

if [ -n "$missing_tools" ]; then
    echo "Missing required tools:$missing_tools"
    echo "Install them with: apt update && apt install -y speedtest-cli jq iputils-ping iproute2"
    exit 1
fi

# Run main function
main "$@"
