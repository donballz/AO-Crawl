import json
from datetime import datetime
from time import clock
import readThread2 as readThread
from os.path import exists
from emailMe import email_me
from altAdjust import alt_adjust


def get_data(tnum):
	ind = open(str(tnum) + '.json', 'r')
	line = ind.readline()
	return json.loads(line)


def parse_date(str_date, str_today):
	today = datetime.strptime(str_today, '%m/%d/%Y')
	if str_date[:9] == "Yesterday":
		time = today
		time = time.replace(day=time.day - 1)
	elif str_date[:5] == "Today":
		time = today
	else:
		time = datetime.strptime(str_date, '%m-%d-%Y, %I:%M %p')
	return time.date()


def first_post(thread_dict):
	firsts = {}
	for post in thread_dict["Posts"]:
		if post["Poster"] not in firsts:
			date = parse_date(post["PostTime"])
			firsts[post["Poster"]] = date
	return firsts


def most_quoted(thread_dict, alt=0):
	quoted = {}
	if alt != 0:
		alts = alt_adjust()
	for post in thread_dict["Posts"]:
		for poster in post["Quoted"]:
			if alt == 0 or poster not in alts:
				final = poster
			else:
				final = alts[poster]
			if final in quoted:
				quoted[final] += 1
			else:
				quoted[final] = 1
	return quoted


def posts_per_day(thread_dict):
	days = {}
	for post in thread_dict["Posts"]:
		date = parse_date(post["PostTime"], thread_dict["Date Pulled"])
		if date in days:
			days[date] += 1
		else:
			days[date] = 1
	return days


def who_posted(thread_dict, alt=0):
	posters = {}
	if alt != 0:
		alts = alt_adjust()
	for post in thread_dict["Posts"]:
		if alt == 0 or post["Poster"] not in alts:
			final = post["Poster"]
		else:
			final = alts[post["Poster"]]
		if final in posters:
			posters[final] += 1
		else:
			posters[final] = 1
	return posters


def emote_only(thread_dict):
	emotes = {}
	for post in thread_dict["Posts"]:
		# check if post is one 'word'
		if len(post["Post"].split()) == 1:
			# check if word is an emoticon
			if post["Post"][-5:-2] == 'gif':  # curly braces were added to all emoticons
				# check if single emoticon
				if post["Post"][0] == '{' and post["Post"].find('{', 2) == -1:
					if post["Post"] in emotes:
						emotes[post["Post"]] += 1
					else:
						emotes[post["Post"]] = 1
	return emotes


def posts_pppd(thread_dict):
	days = {}
	for post in thread_dict["Posts"]:
		date = parse_date(post["PostTime"], thread_dict["Date Pulled"])
		if date in days:
			if post["Poster"] in days[date]:
				days[date][post["Poster"]] += 1
			else:
				days[date][post["Poster"]] = 1
		else:
			days[date] = {post["Poster"]: 1}
	return days


def day_winner(thread_dict, alt=0):
	winners = {}
	days = posts_pppd(thread_dict)
	if alt != 0:
		alts = alt_adjust()
	for day in days:
		winmax, winner = 0, "NA"
		for poster in days[day]:
			if days[day][poster] > winmax:
				winmax, winner = days[day][poster], poster
		if alt == 0 or winner not in alts:
			final = winner
		else:
			final = alts[winner]
		if final in winners:
			winners[final] += 1
		else:
			winners[final] = 1
	return winners


def linus_to_who(thread_dict):
	count, i = [[0, 0]], 0
	date = datetime.today().date()
	for post in thread_dict["Posts"]:
		cur_date = parse_date(post["PostTime"], thread_dict["Date Pulled"])
		if date != cur_date:
			i += 1
			date = cur_date
			count.append([0, 0])
		if post["Poster"] == "Linus":
			count[i][0] += 1
		elif post["Poster"] == "CindyLou Who":
			count[i][1] += 1
	return count


def print_dict(my_dict):
	for key in my_dict:
		print key, ':', my_dict[key]


def print_pct_thread(my_dict, posts):
	for key in my_dict:
		pct = round(100 * float(my_dict[key]) / posts, 2)
		if pct >= 0.01:
			print key, ':', my_dict[key], ',', pct, '%'


def print_thread(thread_dict):
	i = 1
	for post in thread_dict["Posts"]:
		print i, ':', post["Poster"], ':', post["Post"].encode('utf-8')
		print '\n'
		i += 1


def main():
	tnum, page_start = 101562, 1585
	if not exists(str(tnum) + '.json'):
		readThread.output_thread(tnum, page_start)
	thread_dict = get_data(tnum)

	#print_thread(thread_dict)
	#print_dict(most_quoted(thread_dict))
	#print_dict(posts_per_day(thread_dict))
	#print_dict(who_posted(thread_dict))
	#print_dict(emote_only(thread_dict))
	#print_dict(day_winner(thread_dict))

	for j in linus_to_who(thread_dict):
		print j[0], j[1]

	email_me(0)


now = clock()
main()
print '\n', clock() - now
