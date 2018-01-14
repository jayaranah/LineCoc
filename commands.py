# -*- coding: utf-8 -*-
import sys, time, random
import MySQLdb
from main_profile import cocapi

reload(sys)
sys.setdefaultencoding('utf-8')

db = MySQLdb.connect(host="localhost",user="root",passwd="password",db="cocapi")
db.autocommit(True)
cur = db.cursor()

g_coc = cocapi()

class commands:
    def __init__(self): #variables
        self.owner = "u6727192357ee29270ce0f7805e67073f"
        self.season_end = 1517201677
        self.rname = "-coc "
        self.base_help = ["help","rname"]
        self.member_help = ["season_end",
                            "help",
                            "link me to #",
                            "unlink me",
                            "unlink me from all",
                            "unlink me from #",
                            "unlink me from number(s)",
                            "show my #",
                            "show contact of #",
                            "show # of contact",
                            "show # of contacts",
                            "show names linked group",
                            "show number linked group",
                            "show number linked all",
                            "hash #",
                            "hash me",
                            "hash me number(s)",
                            "hash contact (number)",
                            "hash contacts (number)"]
        self.owner_help = ["show names linked all",
                            "announcement groupcast",
                            "secret groupcast"]
        self.uids = [] #uid
        self.tags = [] #tag
        self.players = [] #tag
        self.aa_default = 3
        self.accounts_allowed = {} #uid:number
        self.last_seen = {} #uid:[gid,time,name]
        self.contacts = {} #uid:[gid,reason,number] if number==0, thats means unlimited
                            #some reasons will have 4 elements in the list

### CHAT COMMANDS ###

    #returns a string
    def normaliseHash(raw_hash):
        player_hash = raw_hash.upper()
        if player_hash.find(" ") != -1:
            space = player_hash.find(" ")
            player_hash = player_hash[:space]
        player_hash = player_hash.replace("0","O").replace("1","I")
        return player_hash

    #returns a list of numbers in ascending order
    def numberTextToList(text):
        numbertext = ""
        i = 0
        while i < len(text):
            try:
                numbertext += str(int(text[i]))
            except ValueError:
                numbertext += " "
            i += 1
        nlist = numbertext.split()
        numbers = [int(n) for n in nlist]
        set_num = set(numbers)
        if 0 in set_num:
            set_num.remove(0)
        numbers = list(set_num)
        numbers.sort()
        return numbers

    #returns a string
    def mainHelpMessage(sender, owner_name):
        #create help menu
        string = "##HELP##\n(Brackets are optional)\n"
        #add basic menu
        for bh in self.base_help:
            string += "\n%s" % bh
        string += "\n"
        #add member help
        for mh in self.member_help:
            string += "\n%s%s" % (self.rname, mh)
        #add owner help if owner
        if sender == self.owner:
            for oh in self.owner_help:
                string += "\n%s%s" % (self.rname, oh)
        else:
            string += "\n\n If the bot is not working, check it's status message. For more info, message %s." % owner_name
        return string

    #returns a string
    def timeToSeasonEndMessage(end_time):
        end = end_time
        now = time.time()
        time_left = end-now
        if time_left < 60:
            return "Season has ended."
        else:
            m, s = divmod(time_left, 60)
            h, m = divmod(m, 60)
            d, h = divmod(h, 24)
            if d == 0:
                if h == 0:
                    string = "Season ends in: %dm." % m
                else:
                    string = "Season ends in: %dh %dm." % (h,m)
            else:
                string = "Season ends in: %dd %dh." % (d,h)
            return string

    #returns a string
    def linkToTag(raw_hash,mid):
        n_accounts = self.uids.count(mid) #number of accounts linked
        if mid in self.accounts_allowed.keys():
            aa = self.accounts_allowed[mid]
        else:
            aa = self.aa_default
        #aa is accounts allowed
        if n_accounts < aa:
            player_hash = self.normaliseHash(raw_hash)
            if player_hash in self.tags:
                return "Someone is already linked to this #."
            else:
                player = g_coc.player_info(player_hash)
                if g_coc.statusCode == 200:
                    query = "INSERT INTO `linkedPlayers` (`uid`,`tag`) VALUES ('%s','%s')" % (mid, player_hash)
                    cur.execute(query)
                    self.uids.append(mid)
                    self.tags.append(player_hash)
                    if player_hash not in self.players:
                        query = "INSERT INTO `players` (`tag`) VALUES ('%s')" % player_hash
                        cur.execute(query)
                        self.players.append(player_hash)
                    return "You have been linked to %s (%s/%s)." % (player_hash,n_accounts+1,aa)
                elif g_coc.statusCode == 404:
                    return "%s is not a valid #." % player_hash
                else:
                    return g_coc.statusReasons[g_coc.statusCode]
        else:
            return "You are already linked to your maximum number of #s allowed.\n(%s)" % aa

    #returns a string
    def unlinkFromTagByNumber(number_list,mid):
        if mid in self.uids:
            n_accounts = self.uids.count(mid)
            allowed_numbers = [nl for nl in number_list if nl <= n_accounts]
            if len(allowed_numbers) == 0:
                return "You must include at least one number that corresponds to a # you are linked to."
            else:
                uid_indexes = [i for i in range(len(self.uids)) if self.uids[i] == mid]
                tag_indexes = [uid_indexes[an-1] for an in allowed_numbers]
                tag_indexes.reverse() #because itll get shorter
                unlinked_tags = []
                for ti in tag_indexes:
                    unlinked_tags.append(self.tags[ti])
                    query = "DELETE FROM linkedPlayers WHERE tag = '%s'" % self.tags[ti]
                    cur.execute(query)
                    del self.tags[ti]
                    del self.uids[ti]
                string = "You have been unlinked from:\n"
                for ut in unlinked_tags:
                    string += "\n%s" % ut
                return string
        else:
            return "You are not linked to a #."

    #returns a string
    def unlinkFromTagByTag(tag,mid):
        if mid in self.uids:
            if tag in self.tags:
                index = self.tags.index(tag)
                if self.uids[index] == mid:
                    query = "DELETE FROM linkedPlayers WHERE tag = '%s'" % tag
                    cur.execute(query)
                    del self.uids[index]
                    del self.tags[index]
                    return "You have been unlinked from %s." % tag
                else:
                    return "You are not linked to this tag."
            else:
                return "You are not linked to this tag."
        else:
            return "You are not linked to a #."

    #returns a list of tags
    def showTagsListOfUid(mid):
        tags = [self.tags[i] for i in range(len(self.uids)) if self.uids[i] == mid]
        return tags

    #returns a list of messages
    def makeAndSplitListMessage(start,mlist): 
        if (len(start) > 2000) or (len(max(mlist, key=len)) > 2000):
            return ["Argument is too long."]
        else:
            messages = []
            string = start
            length = 0
            i = 0
            while i < len(mlist):
                if len(string+mlist[i]) > 2000:
                    messages.append(string)
                    string = mlist[i]
                else:
                    string += mlist[i]
                i += 1
            messages.append(string)
            return messages

### NON CHAT COMMANDS - FOR UPDATING TABLES###

    def pullLinkedPlayers(self):
        try:
            self.uids = []
            self.tags = []
            cur.execute("SELECT * FROM linkedPlayers")
            for row in cur.fetchall():
                self.uids.append(row[0]) #uid
                self.tags.append(row[1]) #tag
            return "ok"
        except Exception as e:
            return e

    def pullPlayers(self):
        try:
            self.players = []
            cur.execute("SELECT * FROM players")
            for row in cur.fetchall():
                self.players.append(row[0]) #uid
            return "ok"
        except Exception as e:
            return e

    def pullAccountsAllowed(self):
        try:
            self.accounts_allowed = {}
            cur.excecute("SELECT * FROM accountsAllowed")
            for row in cur.fetchall():
                self.accounts_allowed[row[0]] = int(row[1]) # uid:number
            return "ok"
        except Exception as e:
            return e

    def pullAllNecessary(self):
        response = []
        response.append(pullLinkedPlayers())
        response.append(pullPlayers())
        response.append(pullAccountsAllowed())
        result = ""
        #check whether any errors
        for r in response:
            result = r
            if r != "ok":
                break
        return result

    def saveLastSeen(self):
        try:
            cur.execute("TRUNCATE TABLE lastSeen")
            for uid in self.last_seen.keys():
                query = 'INSERT INTO `lastSeen` (`uid`,`gid`,`time`,`name`) VALUES ("%s","%s","%s","%s")'
                tlist = [uid, self.last_seen[uid][0], self.last_seen[uid][1], self.last_seen[uid][2]]
                tup = tuple(tlist)
                cur.execute(query, tup)
            return "ok"
        except Exception as e:
            return e

    def pullLastSeen(self):
        try:
            self.last_seen = {}
            cur.execute("SELECT * FROM lastSeen")
            for row in cur.fetchall():
                self.last_seen[row[0]] = [row[1],row[2],row[3]]
            return "ok"
        except Exception as e:
            return e

    def enforceAaChanges(self):
        try:
            mids = self.accounts_allowed.keys()
            for mid in mids:
                uid_indexes = [i for i in range(len(self.uids)) if self.uids[i] == mid]
                extra = len(uid_indexes) - self.accounts_allowed[mid]
                while extra > 0:
                    tag = self.tags[uid_indexes[-1]]
                    del self.uids[uid_indexes[-1]]
                    del self.tags[uid_indexes[-1]]
                    query = "DELETE FROM linkedPlayers WHERE tag = '%s'" % tag
                    cur.execute(query)
                    extra = extra -1
            return "ok"
        except Exception as e:
            return e

    def removeDefaultAa(self):
        try:
            query = "DELETE FROM accountsAllowed WHERE number = '%s'" % self.aa_default
            cur.execute(query)
            aa_keys = self.accounts_allowed.keys()
            for ak in aa_keys:
                aa = self.accounts_allowed[ak]
                if aa == aa_default:
                    del self.accounts_allowed[ak]
            return "ok"
        except Exception as e:
            return e