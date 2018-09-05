when CLIENT_ACCEPTED {
	#
	# This rule is intended to provide inbound blackhole DNS to blacklisted origin countries.
	# A datagroup named 'blacklist' is assumed where the country codes are entered in lowercase.
	# The log example below is strictly for testing purposes.
	#

	if {[class match [string tolower [whereis [IP::remote_addr] country]] contains blacklist ]} {
		#log local0. "blacklist making request - dropping"
		drop
	}
}
