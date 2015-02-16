def alt_adjust():
	ind = open('altAdjust.csv', 'r')
	alts = {}
	for line in ind:
		alt_tuple = line.split(',')
		if len(alt_tuple) == 2:
			alts[alt_tuple[0]] = alt_tuple[1]
		else:
			final = ""
			for alt in alt_tuple:
				if alt != alt_tuple[-1]:
					final += alt + ','
			alts[final[:-1]] = alt_tuple[-1]
	return alts
