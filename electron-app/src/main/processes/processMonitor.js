const si = require('systeminformation');

class ProcessMonitor {
  constructor() {
    this.knownProcesses = new Map();
    this.isMonitoring = false;
    this.monitoringInterval = null;
    this.checkInterval = 2000; // Check every 2 seconds
  }

  /**
   * Get all running processes
   */
  async getAllProcesses() {
    try {
      const processes = await si.processes();
      return processes.list.map(proc => ({
        pid: proc.pid,
        name: proc.name,
        command: proc.command,
        cpu: proc.cpu,
        mem: proc.mem,
        started: proc.started,
      }));
    } catch (error) {
      console.error('Error getting processes:', error);
      return [];
    }
  }

  /**
   * Get process information by PID
   */
  async getProcessInfo(pid) {
    try {
      const processes = await si.processes();
      const proc = processes.list.find(p => p.pid === pid);
      if (proc) {
        return {
          pid: proc.pid,
          name: proc.name,
          command: proc.command,
          cpu: proc.cpu,
          mem: proc.mem,
          started: proc.started,
        };
      }
      return null;
    } catch (error) {
      console.error('Error getting process info:', error);
      return null;
    }
  }

  /**
   * Start monitoring process launches and terminations
   */
  startMonitoring(onProcessLaunch, onProcessTermination) {
    if (this.isMonitoring) {
      return;
    }

    this.isMonitoring = true;
    
    // Get initial process list
    this.getAllProcesses().then(processes => {
      processes.forEach(proc => {
        this.knownProcesses.set(proc.pid, proc);
      });
    });

    this.monitoringInterval = setInterval(async () => {
      try {
        const currentProcesses = await this.getAllProcesses();
        const currentPids = new Set(currentProcesses.map(p => p.pid));

        // Check for new processes
        for (const proc of currentProcesses) {
          if (!this.knownProcesses.has(proc.pid)) {
            this.knownProcesses.set(proc.pid, proc);
            if (onProcessLaunch) {
              onProcessLaunch(proc);
            }
          }
        }

        // Check for terminated processes
        for (const [pid, proc] of this.knownProcesses.entries()) {
          if (!currentPids.has(pid)) {
            this.knownProcesses.delete(pid);
            if (onProcessTermination) {
              onProcessTermination(proc);
            }
          }
        }
      } catch (error) {
        console.error('Error in process monitoring:', error);
      }
    }, this.checkInterval);
  }

  /**
   * Stop monitoring processes
   */
  stopMonitoring() {
    this.isMonitoring = false;
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
  }
}

module.exports = ProcessMonitor;

