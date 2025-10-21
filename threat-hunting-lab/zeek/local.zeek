##! Local site policy. Customize as appropriate.

@load base/frameworks/software
@load base/protocols/conn
@load base/protocols/dns
@load base/protocols/http
@load base/protocols/ssl
@load base/protocols/ssh
@load base/protocols/smb
@load policy/protocols/smb

# Enable JSON logging for easier parsing
@load policy/tuning/json-logs.zeek

# Load additional analysis scripts for threat detection
@load base/frameworks/notice
@load base/frameworks/intel

# Custom notices for suspicious activity
redef Notice::emailed_types += {
    Conn::Content_Gap,
    HTTP::SQL_Injection_Attacker,
    HTTP::SQL_Injection_Victim,
};

# Detect long connections (potential C2)
redef Conn::duration_threshold = 1hrs;

# Log more HTTP details
redef HTTP::default_capture_password = T;

# Enable file analysis
@load frameworks/files/hash-all-files
@load frameworks/files/detect-MHR

# Custom event to detect beaconing
event connection_state_remove(c: connection)
    {
    if ( c$duration > 5mins && c$orig$num_pkts > 100 )
        {
        print fmt("Long-lived connection detected: %s -> %s", c$id$orig_h, c$id$resp_h);
        }
    }
