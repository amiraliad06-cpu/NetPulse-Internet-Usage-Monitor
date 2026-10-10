import time
import threading
import socket
import psutil
import database

class NetworkMonitor:
    def __init__(self):
        self.selected_interface = "All Interfaces"  # Can be set to a specific adapter name
        
        # Real-time speeds (bytes per second)
        self.download_speed = 0.0
        self.upload_speed = 0.0
        
        # Current minute's in-memory accumulators
        self.current_minute_download = 0
        self.current_minute_upload = 0
        
        # Previous counter readings
        self.last_recv_bytes = 0
        self.last_sent_bytes = 0
        
        # Connection metadata
        self.active_ip = "127.0.0.1"
        self.active_interface = "All Interfaces"
        self.connected = False
        
        # Uptime and threading
        self.start_time = time.time()
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        
        # Check active IP/interface immediately on creation
        self.update_network_info()

    def start(self):
        """Start the background monitoring thread."""
        with self.lock:
            if not self.running:
                self.running = True
                self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
                self.thread.start()
                print("Network Monitor thread started.")

    def stop(self):
        """Stop the background monitoring thread."""
        with self.lock:
            self.running = False

    def get_uptime(self):
        """Return application uptime in 'Hh Mm Ss' format."""
        elapsed = int(time.time() - self.start_time)
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        return f"{hours}h {minutes}m {seconds}s"

    def get_interfaces(self):
        """Retrieve a list of available network interfaces with non-loopback IPs."""
        interfaces = ["All Interfaces"]
        try:
            addrs = psutil.net_if_addrs()
            io_counters = psutil.net_io_counters(pernic=True)
            for name in addrs.keys():
                # Only include interfaces that actually exist in the IO counters and are active
                if name in io_counters:
                    interfaces.append(name)
        except Exception as e:
            print(f"Error listing interfaces: {e}")
        return interfaces

    def set_interface(self, name):
        """Change the monitored interface and reset tracking counters to avoid speed spikes."""
        with self.lock:
            interfaces = self.get_interfaces()
            if name in interfaces:
                self.selected_interface = name
                self.last_recv_bytes = 0
                self.last_sent_bytes = 0
                print(f"Monitored interface changed to: {name}")
                return True
            return False

    def update_network_info(self):
        """Update active IP, active interface, and internet connection status."""
        # 1. Check internet connection by trying to connect to Google DNS
        connected = False
        ip = "127.0.0.1"
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(1.5)
            # Try to connect to a public IP - 8.8.8.8 on port 53 (DNS)
            s.connect(("8.8.8.8", 53))
            ip = s.getsockname()[0]
            s.close()
            connected = True
        except Exception:
            connected = False
            # If Google DNS fails, try to get local hostname IP as fallback
            try:
                ip = socket.gethostbyname(socket.gethostname())
            except Exception:
                ip = "127.0.0.1"

        # 2. Map local IP to active interface name
        active_interface = "All Interfaces"
        if ip != "127.0.0.1":
            try:
                addrs = psutil.net_if_addrs()
                for name, info in addrs.items():
                    for addr in info:
                        if addr.family == socket.AF_INET and addr.address == ip:
                            active_interface = name
                            break
            except Exception:
                pass

        with self.lock:
            self.connected = connected
            self.active_ip = ip
            self.active_interface = active_interface

    def _get_io_counters(self):
        """Retrieve total bytes received and sent for the currently selected interface."""
        try:
            if self.selected_interface == "All Interfaces":
                counters = psutil.net_io_counters()
                return counters.bytes_recv, counters.bytes_sent
            else:
                counters = psutil.net_io_counters(pernic=True)
                if self.selected_interface in counters:
                    ctr = counters[self.selected_interface]
                    return ctr.bytes_recv, ctr.bytes_sent
                else:
                    # Fallback if interface disconnected
                    counters = psutil.net_io_counters()
                    return counters.bytes_recv, counters.bytes_sent
        except Exception as e:
            print(f"Error getting network counters: {e}")
            return 0, 0

    def _monitor_loop(self):
        """Background monitoring loop running once per second."""
        second_counter = 0
        
        while self.running:
            start_time_tick = time.time()
            
            # 1. Fetch current network statistics
            recv_bytes, sent_bytes = self._get_io_counters()
            
            with self.lock:
                # 2. Check for first run or interface reset
                if self.last_recv_bytes == 0 and self.last_sent_bytes == 0:
                    self.last_recv_bytes = recv_bytes
                    self.last_sent_bytes = sent_bytes
                    self.download_speed = 0.0
                    self.upload_speed = 0.0
                else:
                    # 3. Compute deltas
                    delta_down = recv_bytes - self.last_recv_bytes
                    delta_up = sent_bytes - self.last_sent_bytes
                    
                    # 4. Handle adapter reboots or resets (negative deltas)
                    if delta_down < 0 or delta_up < 0:
                        delta_down = 0
                        delta_up = 0
                        
                    # 5. Calculate real-time speed (bytes per second)
                    self.download_speed = float(delta_down)
                    self.upload_speed = float(delta_up)
                    
                    # 6. Accumulate into current minute's log
                    self.current_minute_download += delta_down
                    self.current_minute_upload += delta_up
                    
                    # 7. Update last bytes
                    self.last_recv_bytes = recv_bytes
                    self.last_sent_bytes = sent_bytes

            second_counter += 1
            
            # 8. Every 60 seconds, save accumulated minute logs to SQLite
            if second_counter >= 60:
                with self.lock:
                    down_to_save = self.current_minute_download
                    up_to_save = self.current_minute_upload
                    # Reset the accumulators
                    self.current_minute_download = 0
                    self.current_minute_upload = 0
                
                # Write to DB in worker thread
                database.log_usage(down_to_save, up_to_save)
                second_counter = 0

            # 9. Every 10 seconds, refresh connection metadata
            if second_counter % 10 == 0:
                self.update_network_info()
                
            # Precision sleeping to align as close to 1 second as possible
            elapsed = time.time() - start_time_tick
            sleep_time = max(0.1, 1.0 - elapsed)
            time.sleep(sleep_time)

    def get_live_data(self):
        """Retrieve real-time consolidated stats for the API, combining DB history and current minute memory."""
        # Query persistent DB totals
        db_today = database.get_today_totals()
        db_month = database.get_month_totals()
        
        with self.lock:
            speed_down = self.download_speed
            speed_up = self.upload_speed
            mem_down = self.current_minute_download
            mem_up = self.current_minute_upload
            connected = self.connected
            ip_addr = self.active_ip
            active_iface = self.active_interface
            sel_iface = self.selected_interface
            uptime = self.get_uptime()

        # Combine historical DB stats + the running (unwritten) minute bytes for instant live accuracy
        today_download = db_today["download_bytes"] + mem_down
        today_upload = db_today["upload_bytes"] + mem_up
        month_download = db_month["download_bytes"] + mem_down
        month_upload = db_month["upload_bytes"] + mem_up
        
        return {
            "connected": connected,
            "ip_address": ip_addr,
            "active_interface": active_iface,
            "selected_interface": sel_iface,
            "uptime": uptime,
            "download_speed_bps": speed_down,
            "upload_speed_bps": speed_up,
            "today_download_bytes": today_download,
            "today_upload_bytes": today_upload,
            "month_download_bytes": month_download,
            "month_upload_bytes": month_upload
        }
