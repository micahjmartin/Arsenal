"""
    This module willl send a syslog whenever a beacon calls back
    https://github.com/degenerat3/sawmill
    Author: Micah Martin
"""
import socket
from .integration import Integration


class SyslogIntegration(Integration): # pylint: disable=too-few-public-methods
    """
    Configuration:
    """

    def __init__(self, config):
        """
        Initialize the integration.
        """
        self.config = config
        self.host = config.get("host", False)
        self.port = config.get("port", 5000)

    def __str__(self):
        """
        Return the integration name as the string.
        """
        return 'syslog-integration'

    def run(self, event_data, **kwargs):
        """
        Post an update to the syslog server
        """
        if not self.host:
            return False
        event = event_data.get("event")
        if event != "session_checkin":
            return False
        # Try to get the agent string
        name = event_data.get("session", {}).get("agent_version", "Arsenal")

        # Get the facts
        facts = event_data.get("target", {}).get("facts", {})
        # Stolen from cli.getTarget
        ip_addrs = []
        for iface in facts.get('interfaces', []):
            for addr in iface.get('ip_addrs', []):
                if not addr.startswith("127."):
                    ip_addrs.append(addr)
        if not ip_addrs:
            # If we dont have an IP, then we have nothing to update
            return False

        message = ""
        for ip in ip_addrs:
            message += "{} BOXACCESS {} Session callback received to Arsenal\n".format(name, ip)

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            s.sendall(message)
            s.close()
            return True
        except socket.error:
            return False
