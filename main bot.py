# -*- coding: utf-8 -*-
from LineAlpha import LineClient
from LineAlpha.LineApi import LineTracer
from LineAlpha.LineThrift.ttypes import Message, TalkException
from thrift.Thrift import TType, TMessageType, TException, TApplicationException
from LineAlpha.LineThrift.TalkService import Client
from multiprocessing import Process
from commands import commands
import sys, os, time, atexit

reload(sys)
sys.setdefaultencoding('utf-8')

#NOTE mid and uid are used interchangably

do = commands()

#Pull all data from tables
setup []
setup.append(do.pullAllNecessary())
setup.append(do.pullLastSeen())
setup.append(do.enforceAaChanges())
setup.append(do.removeDefaultAa())
for s in setup:
    if s != "ok":
        raise Exception(s)
print "Setup Complete."


##LOGIN##
token = "token"
client = LineClient()
client._tokenLogin(token)

profile, setting, tracer = client.getProfile(), client.getSettings(), LineTracer(client)
offbot, messageReq, wordsArray, waitingAnswer = [], {}, {}, {}

print client._loginresult()

### IMPORTANT FUNCTIONS ###

def sendMessage(to, text, contentMetadata={}, contentType=0):
    mes = Message()
    mes.to, mes.from_ = to, profile.mid
    mes.text = text

    mes.contentType, mes.contentMetadata = contentType, contentMetadata
    if to not in messageReq:
        messageReq[to] = -1
    messageReq[to] += 1
    client._client.sendMessage(messageReq[to], mes)

def makeSendMainProfile(player_hash, to):
    name = str(random.randint(10000,99999))
    path = ""
    response = g_coc.makeProfile(player_hash, name=name, path=path)
    if response == 200:
        client.sendImage(to_=to, path=(name+".jpg"))
        os.remove(name+".jpg")
    elif response == 404:
        sendMessage(to=to, text="%s is not a valid #." % player_hash)
    else:
        sendMessage(to=to, text=g_coc.statusReasons[response])

def exitHandler():
    do.saveLastSeen()
atexit.register(exitHandler)

### MAIN BOT OPERATIONS ###

def NOTIFIED_ADD_CONTACT(op):
    client.findAndAddContactsByMid(op.param1)
    sendMessage(to=do.owner, text=(client.getContact(op.param1).displayName+" added you as a friend."))
    sendMessage(to=do.owner, text="", contentMetadata={"mid":op.param1}, contentType=13)
    name = client.getContact(op.param1).displayName
    do.last_seen[op.param1] = ["add contact", time.time(), name]
tracer.addOpInterrupt(5, NOTIFIED_ADD_CONTACT)

def NOTIFIED_INVITE_INTO_GROUP(op):
    if profile.mid in op.param3:
        try:
            client.acceptGroupInvitation(op.param1)
            sendMessage(to=op.param1, text="Thanks for inviting me. I cannot kick invite, or change group settings. For more information, type '-coc help'. To make me leave, type '-coc @bye'.")
        except Exception as e:
            print e
    name = client.getContact(op.param2).displayName
    do.last_seen[op.param2] = [op.param1, time.time(), name]
tracer.addOpInterrupt(13, NOTIFIED_INVITE_INTO_GROUP)

def NOTIFIED_INVITE_INTO_ROOM(op):
    sendMessage(to=msg.to, text="Sorry, I don't work in rooms.")
    client.leaveRoom(op.param1)
    name = client.getContact(op.param2).displayName
    do.last_seen[op.param2] = ["room", time.time(), name]
tracer.addOpInterrupt(22, NOTIFIED_INVITE_INTO_ROOM)

def NOTIFIED_READ_MESSAGE(op):
    name = client.getContact(op.param2).displayName
    do.last_seen[op.param2] = [op.param1, time.time(), name]
tracer.addOpInterrupt(55, NOTIFIED_READ_MESSAGE)

def RECEIVE_MESSAGE(op):
    msg = op.message
    if msg.contentType == 0:
        try:
            text = msg.text.rstrip()
            if text.lower() == "help":
                sendMessage(to=msg.to, text="Type '%shelp' for a detailed help list." % do.rname)
            elif text.lower() in ["rname","responsename"]:
                sendMessage(to=msg.to, text=do.rname)
            elif text[:len(do.rname)] == do.rname:
                text = text[len(do.rname):]
                if text.lower() == "season end":
                    se = do.timeToSeasonEndMessage(do.season_end)
                    sendMessage(to=msg.to, text=se)
                elif text.lower() == "help":
                    name = client.getContact(do.owner).displayName
                    mhm = do.mainHelpMessage(msg.from_, name)
                    sendMessage(to=msg.to, text=mhm)
                elif text[:12].lower() == "link me to #":
                    raw_hash = text[11:]
                    ltt = do.linkToTag(raw_hash,msg.from_)
                    sendMessage(to=msg.to,text=ltt)
                elif text.lower() == "unlink me":
                    #unlink from last tag
                    tags = do.showTagsListOfUid(msg.from_)
                    if len(tags) == 0:
                        sendMessage(to=msg.to,text="You are not linked to a #.")
                    else:
                        number_list = [len(tags)]
                        uftbn = do.unlinkFromTagByNumber(number_list,msg.from_)
                        sendMessage(to=msg.to, text=uftbn)
                elif text.lower() == "unlink me from all":
                    tags = do.showTagsOfUid(msg.from_)
                    if len(tags) == 0:
                        sendMessage(to=msg.to,text="You are not linked to a #.")
                    else:
                        numbers = range(1,len(tags)+1)
                        uftbn = do.unlinkFromTagByNumber(numbers,msg.from_)
                        sendMessage(to=msg.to, text=uftbn)
                elif text[:16].lower() == "unlink me from #":
                    raw_hash = text[15:]
                    player_hash = do.normaliseHash(raw_hash)
                    uftbt = do.unlinkFromTagByTag(player_hash,msg.from_)
                    sendMessage(to=msg.to, text=uftbt)
                elif text[:14].lower() == "unlink me from":
                    numbertext = text[14:]
                    nlist = do.numberTextToList(numbertext)
                    uftbn = do.unlinkFromTagByNumber(nlist,msg.from_)
                    sendMessage(to=msg.to, text=uftbn)
                elif text.lower() in ["show my #","show my #s"]:
                    if mid in self.accounts_allowed.keys():
                        aa = self.accounts_allowed[mid]
                    else:
                        aa = self.aa_default
                    tags = do.showTagsListOfUid(msg.from_)
                    if len(tags) == 0:
                        string = "You are not linked to a #. (0/%s)" % aa
                    else:
                        string = "You are linked to:"
                        for tag in tags:
                            string += "\n%s" % tag
                        string += "\n(%s/%s)" % (len(tags),aa)
                    sendMessage(to=msg.to, text=string)
                elif text[:17].lower() == "show contact of #":
                    raw_hash = text[16:]
                    player_hash = do.normaliseHash(raw_hash)
                    if player_hash in self.tags:
                        tag_index = self.tags.index(player_hash)
                        uid = self.uids[tag_index]
                        sendMessage(to=msg.to, text="", contentMetadata={"mid":uid}, contentType=13)
                    else:
                        sendMessage(to=msg.to, text="No one is linked to %s." % player_hash)
                elif text.lower() == "show # of contact": #reason = "show #"
                    do.contacts[msg.from_] = [msg.to,"show #",1]
                    sendMessage(to=msg.to, text="Send a contact.")
                elif text.lower() == "show # of contacts": #reason = "show #"
                    do.contacts[msg.from_] = [msg.to,"show #",0]
                    sendMessage(to=msg.to, text="Send contacts.")
                elif text.lower() == "show names linked group":
                    group = client.getGroup(msg.to)
                    gmids = [contact.displayName for contact in group.members]
                    gnames = [contact.mid for contact in group.members]
                    #nal is number of accounts linked
                    nal = [self.uids.count(gmid) for gmid in gmids if gmid in self.uids]
                    #lnames is linked names
                    lnames = [gnames[i] for i in range(len(gnames)) if gmids[i] in self.uids]
                    mlist = ["\n%s (%s)" % (lnames[i],nal[i]) for i in range(len(nal))]
                    start_message = "Linked players in %s:\n" % group.name
                    messages = do.makeAndSplitListMessage(start_message,mlist)
                    for m in messages:
                        sendMessage(to=msg.to, text=m)
                elif text.lower() == "show number linked group":
                    group = client.getGroup(msg.to)
                    gmids = [contact.displayName for contact in group.members]
                    gnames = [contact.mid for contact in group.members]
                    linked_mids = [gmid in gmids if gmid in self.uids]
                    luids = len(linked_mids)
                    ltags = 0
                    for lm in linked_mids:
                        c = do.showTagsListOfUid(lm)
                        ltags += len(c)
                    sendMessage(to=msg.to, text="%s people are linked to %s tags in this group." % (luids, ltags))
                elif text.lower() == "show number linked all":
                    luids = len(set(self.uids))
                    ltags = len(self.tags)
                    sendMessage(to=msg.to, text="%s people are linked to %s tags overall." % (luids, ltags))
                elif text[:6].lower() == "hash #":
                    player_hash = do.normaliseHash(text[5:])
                    Process(target=makeSendMainProfile, args=(player_hash,msg.to)).start()
                elif text.lower() == "hash me":
                    tags = do.showTagsListOfUid(msg.from_)
                    if len(tags) == 0:
                        sendMessage(to=msg.to, text="You are not linked to a #.")
                    else:
                        tag = tags[0]
                        Process(target=makeSendMainProfile, args=(tag,msg.to)).start()
                elif text[:7].lower() == "hash me":
                    numbertext = text[7:]
                    numbers = do.numberTextToList(numbertext)
                    tags = do.showTagsListOfUid(msg.from_)
                    if len(numbers) == 0:
                        sendMessage(to=msg.to, text="You have not included any numbers.")
                    elif len(tags) == 0:
                        sendMessage(to=msg.to, text="You are not linked to a #.")
                    else:
                        use_tags = [tag[i] for i in numbers if i < len(tags)]
                        if len(use_tags) == 0:
                            sendMessage(to=msg.to, text="You have not included any numbers that correspond to a # linked to your account.")
                        else:
                            for ut in use_tags:
                                Process(target=makeSendMainProfile, args=(ut,msg.to)).start()
                elif text.lower() == "hash contact": #reason = "image main_profile"
                    do.contacts[msg.from_] = [msg.to,"image main_profile",1,[1]]
                    #4th element is which tag(s), starting from 1
                    sendMessage(to=msg.to, text="Send a contact.")
                elif text[:12].lower() == "hash contact": #reason = "image main_profile"
                    numbertext = text[12:]
                    #4th element is which tag(s), starting from 1
                    nlist = do.numberTextToList(numbertext)
                    if len(nlist) == 0:
                        nlist = [1]
                    do.contacts[msg.from_] = [msg.to,"image main_profile",1,nlist]
                    sendMessage(to=msg.to, text="Send a contact.")
                elif text.lower() == "hash contacts": #reason = "image main_profile"
                    do.contacts[msg.from_] = [msg.to,"image main_profile",0,[1]]
                    sendMessage(to=msg.to, text="Send contacts.")
                elif text[:13].lower() == "hash contacts": #reason = "image main_profile"
                    numbertext = text[13:]
                    nlist = do.numberTextToList(numbertext)
                    if len(nlist) == 0:
                        nlist = [1]
                    do.contacts[msg.from_] = [msg.to,"image main_profile",0,nlist]
                    sendMessage(to=msg.to, text="Send contacts.")
                elif msg.from_ == do.owner:
                    if text.lower() == "show names linked all":
                        set_uids = set(self.uids)
                        names = [client.getContact(mid).displayName for mid in set_uids]
                        nal = [self.uids.count(mid) for mid in set_uids]
                        mlist = ["\n%s (%s)" % (names[i],nal[i]) for i in range(len(nal))]
                        start = "All linked players:\n"
                        messages = do.makeAndSplitListMessage(start,mlist)
                        for m in messages:
                            sendMessage(to=msg.to, text=m)
                    elif text[:22].lower() == "announcement groupcast":
                        name = client.getContact(do.owner).displayName
                        message = text[22:].rstrip()
                        announcement = "Groupcast from %s:\n\n%s" % (name,message)
                        gids = client.getGroupIdsJoined()
                        for gid in gids:
                            sendMessage(to=gid, text=message)
                    elif text[:16].lower() == "secret groupcast":
                        message = [16:].rstrip()
                        gids = client.getGroupIdsJoined()
                        for gid in gids:
                            sendMessage(to=gid, text=message)
        except Exception as e:
            print e
    elif msg.contentType == 13:
        try:
            if msg.from_ in self.contacts.keys():
                if self.contacts[msg.from_][0] == msg.to:
                    mid = msg.contentMetadata["mid"]
                    reason = self.contacts[msg.from_][1]
                    number = self.contacts[msg.from_][2]
                    if reason == "show #":
                        uid_indexes = [i for i in range(len(self.uids)) if self.uids[i]==mid]
                        tags = [self.tags[ui] for ui in uid_indexes]
                        string = ""
                        for tag in tags:
                            string += "%s\n" tag
                        string = string[:-1]
                        sendMessage(to=msg.to, text=string)
                    elif reason == "image main_profile":
                        numbers = self.contacts[msg.from_][3]
                        uid_indexes = [i for i in range(len(self.uids)) if self.uids[i]==mid]
                        tags = [self.tags[ui] for ui in uid_indexes]
                        r_tags = [tags[n-1] for n in numbers if n <= len(tags)]
                        if len(r_tags) == 0:
                            sendMessage(to=msg.to, text="None of the numbers correspond to a # linked to this contact's account.")
                        else:
                            for rt in r_tags:
                                Process(target=makeSendMainProfile, args=(rt,msg.to)).start()
                    if reason in ["show #","image main_profile"]:
                        if number == 1:
                            del self.contacts[msg.from_]
                        else:
                            self.contacts[msg.from_][2] = number-1
        except Exception as e:
            print e
    name = client.getContact(msg.from_).displayName
    do.last_seen[msg.from_] = [msg.to, time.time(), name]
tracer.addOpInterrupt(26, RECEIVE_MESSAGE)

while True:
    tracer.execute()