# -*- coding: utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

class commands:
	def __init__(self):
		# ALL PERMANENT VARIABLES
		self.responsename = "Bot"
		self.squadname = "bot"
		self.owner = ["u6929f3ed28b8573df488cc02dd82be9c"] #uid
		self.admin = ["u6929f3ed28b8573df488cc02dd82be9c"] # uid
		self.staff = ["u6929f3ed28b8573df488cc02dd82be9c"] #uid
		self.bot = [] #uid
		self.banlist = [] #uid
		self.contact_functions = {} #uid:[gid,reason,amount]
		self.welcome_message = {} #gid:welcome_message
		self.autojoin = "all" #can be all or staff
		
	def getRank(self, uid):
		if uid in self.owner:
			return "owner"
		elif uid in self.admin:
			return "admin"
		elif uid in self.staff:
			return "staff"
		elif uid in self.bot:
			return "bot"
		else:
			return "none"

	def giveStaff(self, uid_promoter, uid_promotee, name_promotee):
		if uid_promoter in self.admin:
			if uid_promotee in self.staff:
				rank = self.getRank(uid_promotee)
				return "%s is already %s." % (name_promotee, rank)
			elif uid.promotee in self.banlist:
				return "Cannot promote to staff; %s is banned." % name_promotee
			else:
				self.staff.append(uid_promotee)
				return "%s has been promoted to staff." % name_promotee
		else:
			return "Cannot promote to staff; you are not admin."
			
	def giveAdmin(self, uid_promoter, uid_promotee, name_promotee):
		if uid_promoter in self.owner:
			if uid_promotee in self.admin:
				rank = self.getRank(uid_promotee)
				return "%s is already %s." % (name_promotee, rank)
			elif uid.promotee in self.banlist:
				return "Cannot promote to admin; %s is banned." % name_promotee
			else:
				self.admin.append(uid_promotee)
				if uid_promotee not in self.staff:
					self.staff.append(uid_promotee)
				return "%s has been promoted to admin." % name_promotee
		else:
			return "Cannot promote to admin; you are not owner."
		
	def giveOwner(self, uid_promoter, uid_promotee, name_promotee):
		if uid_promoter in self.owner:
			if uid_promotee in self.owner:
				return "%s is already owner." % name_promotee
			elif uid.promotee in self.banlist:
				return "Cannot promote to owner; %s is banned." % name_promotee
			else:
				self.owner.append(uid_promotee)
				if uid_promotee not in self.staff:
					self.staff.append(uid_promotee)
				if uid_promotee not in self.admin:
					self.admin.append(uid_promotee)
				return "%s has been promoted to admin." % name_promotee
		else:
			return "Cannot promote to owner; you are not owner."
		
	def giveBot(self, uid_promoter, uid_promotee, name_promotee):
		if uid_promoter in self.admin:
			all = self.owner+self.admin+self.staff+self.bot
			if uid_promotee in all:
				rank = self.getRank(uid_promotee)
				return "%s is already %s." % (name_promotee, rank)
			elif uid.promotee in self.banlist:
				return "Cannot promote to bot; %s is banned." % name_promotee
			else:
				self.bot.append(uid_promotee)
				return "%s has been promoted to bot." % name_promotee
		else:
			return "Cannot promote to bot; you are not admin."
		
	def expel(self, uid_expeller, uid_expellee, name_expellee):
		rank_number = {"owner":1,"admin":2,"bot":3,"staff":4,"none":5}
		#rn means rank_number
		rn_expeller = rank_number[self.getRank(uid_expeller)]
		rn_expellee = rank_number[self.getRank(uid_expellee)]
		if rn_expellee == 5:
			return "%s is not on the bot."
		elif rn_expeller == 1: #owner can expel anyone, even owner
			if uid_expellee in self.staff:
				self.staff.remove(uid_expellee)
			if uid_expellee in self.bot:
				self.bot.remove(uid_expellee)
			if uid_expellee in self.admin:
				self.admin.remove(uid_expellee)
			if uid_expellee in self.owner:
				self.owner.remove(uid_expellee)
			return "%s has been expelled from %s." % (name_expellee, self.getRank(uid_expellee))
		elif rn_expellee > rn_expeller:
			if uid_expellee in self.staff:
				self.staff.remove(uid_expellee)
			if uid_expellee in self.bot:
				self.bot.remove(uid_expellee)
			if uid_expellee in self.admin:
				self.admin.remove(uid_expellee)
			return "%s has been expelled from %s." % (name_expellee, self.getRank(uid_expellee))
		else:
			return "Cannot expel; %s has a higher rank than you." % name_expellee
				
	def ban(self, uid_banner, uid_bannee, name_bannee)
		if uid_banner in self.admin:
			if uid_bannee not in self.banlist:
				self.banlist.append(uid_bannee)
				return "%s has been banned." % name_bannee
			else:
				return "%s is already banned." % name_bannee
		else:
			return "Cannot ban; you are not admin."

	def unban(self, uid_unbanner, uid_unbannee, name_unbannee):
		if uid_unbannee in self.banlist:
			if uid_unbanner in self.admin:
				self.banlist.remove(uid_unbannee)
				return "%s has been unbanned." % name_unbannee
			else:
				return "Cannot unban; you are not admin."
		else:
			return "%s is not banned." % name_unbannee
		
