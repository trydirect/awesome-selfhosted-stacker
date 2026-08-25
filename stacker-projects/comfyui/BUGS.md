[BUG] Cloud VM SSH key uses status_panel mode — can't SSH with local key

Cloud VMs (e.g. comfyui-2601 at 167.233.216.242) list KEY STATUS as "active"
and MODE as "status_panel". Attempting SSH with the local identity file
(`stacker-project-test`) fails with "Permission denied". The status_panel
mode uses Stacker's built-in key, not the user-provided one.
