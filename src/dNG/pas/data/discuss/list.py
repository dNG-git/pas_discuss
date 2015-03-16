# -*- coding: utf-8 -*-
##j## BOF

"""
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?pas;discuss

The following license agreement remains valid unless any additions or
changes are being made by direct Netware Group in a written form.

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc.,
59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;gpl
----------------------------------------------------------------------------
#echo(pasDiscussVersion)#
#echo(__FILEPATH__)#
"""

from time import time

from dNG.pas.data.binary import Binary
from dNG.pas.data.data_linker import DataLinker
from dNG.pas.data.ownable_lockable_write_mixin import OwnableLockableWriteMixin
from dNG.pas.data.subscribable_mixin import SubscribableMixin
from dNG.pas.database.connection import Connection
from dNG.pas.database.lockable_mixin import LockableMixin
from dNG.pas.database.nothing_matched_exception import NothingMatchedException
from dNG.pas.database.instances.data_linker import DataLinker as _DbDataLinker
from dNG.pas.database.instances.discuss_list import DiscussList as _DbDiscussList
from dNG.pas.database.instances.discuss_topic import DiscussTopic as _DbDiscussTopic

class List(DataLinker, LockableMixin, OwnableLockableWriteMixin, SubscribableMixin):
#
	"""
"List" represents a discussion list.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: discuss
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self, db_instance = None):
	#
		"""
Constructor __init__(List)

:param db_instance: Encapsulated SQLAlchemy database instance

:since: v0.1.00
		"""

		DataLinker.__init__(self, db_instance)
		LockableMixin.__init__(self)
		OwnableLockableWriteMixin.__init__(self)
		SubscribableMixin.__init__(self)

		self.total_posts = None
		"""
Number of posts of this and all subjacent lists
		"""
		self.total_topics = None
		"""
Number of topics of this and all subjacent lists
		"""
		self.latest_timestamp = None
		"""
Timestamp of the newest post of this or an subjacent list
		"""
		self.latest_topic_id = None
		"""
Topic ID of the newest post of this or an subjacent list
		"""
		self.latest_author_id = None
		"""
Author ID of the newest post of this or an subjacent list
		"""
		self.latest_preview = None
		"""
Preview of the newest post of this or an subjacent list
		"""
	#

	def _analyze_structure(self, cache_id = None):
	#
		"""
Returns the number of posts of this and all subjacent lists.

:param cache_id: ID used for building the structure SQLAlchemy query and
                 cache its result.

:since: v0.1.00
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._analyze_structure()- (#echo(__LINE__)#)", self, context = "pas_datalinker")

		with self:
		#
			if (cache_id is None): cache_id = "DiscussList:{0}".format(self.local.db_instance.id_main)
			permission_user_id = self.get_permission_user_id()

			DataLinker._analyze_structure(self, cache_id)

			self.latest_timestamp = -1
			self.total_topics = 0
			self.total_posts = 0

			for entry in self.structure_instance.get_structure_list(self.local.db_instance.id):
			#
				is_readable = True

				if (isinstance(entry, OwnableLockableWriteMixin)):
				#
					entry.set_permission_user_id(permission_user_id)
					is_readable = entry.is_readable()
				#

				if (is_readable and (not entry.is_data_attribute_none("topics", "posts"))):
				#
					entry_data = entry.get_data_attributes("time_sortable", "topics", "posts", "last_id_topic", "last_id_author", "last_preview")

					self.total_topics += entry_data['topics']
					self.total_posts += entry_data['posts']

					if (entry_data['last_id_topic'] is not None and entry_data['time_sortable'] > self.latest_timestamp):
					#
						self.latest_timestamp = entry_data['time_sortable']
						self.latest_topic_id = entry_data['last_id_topic']
						self.latest_author_id = entry_data['last_id_author']
						self.latest_preview = entry_data['last_preview']
					#
				#
			#
		#
	#

	def add_post(self, post, topic = None, post_preview = None):
	#
		"""
Add the given post.

:param post: DiscussPost instance
:param topic: DiscussTopic instance
:param post_preview: Post preview

:since: v0.1.00
		"""

		# pylint: disable=protected-access

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.add_post()- (#echo(__LINE__)#)", self, context = "pas_datalinker")

		if (isinstance(post, DataLinker) and post.get_identity() == "DiscussPost"):
		#
			with self:
			#
				post_data = post.get_data_attributes("id", "author_id")

				if (post_data['id'] != self.local.db_instance.id):
				#
					list_data = { "posts": "++" }

					if (isinstance(topic, DataLinker) and topic.get_identity() == "DiscussTopic"):
					#
						list_data['time_sortable'] = time()
						list_data['last_id_topic'] = topic.get_id()
						list_data['last_id_author'] = post_data['author_id']
						list_data['last_preview'] = post_preview
					#

					self.set_data_attributes(**list_data)
				#
			#
		#
	#

	def add_topic(self, topic, post = None, post_preview = None):
	#
		"""
Add the given topic.

:param topic: DiscussTopic instance
:param post: DiscussPost instance
:param post_preview: Post preview

:since: v0.1.00
		"""

		# pylint: disable=protected-access

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.add_topic()- (#echo(__LINE__)#)", self, context = "pas_datalinker")

		if (isinstance(topic, DataLinker) and topic.get_identity() == "DiscussTopic"):
		#
			with self:
			#
				topic_data = topic.get_data_attributes("id", "author_id")

				if (topic_data['id'] != self.local.db_instance.id):
				#
					self.local.db_instance.rel_children.append(topic._get_db_instance())
					topic.set_data_attributes(id_main = self.local.db_instance.id_main)

					topic_data = { "time_sortable": time(),
					               "topics": "++",
					               "last_id_topic": topic_data['id'],
					               "last_id_author": topic_data['author_id'],
					               "last_preview": post_preview
					             }

					if (isinstance(post, DataLinker) and post.get_identity() == "DiscussPost"): topic_data['posts'] = "++"

					self.set_data_attributes(**topic_data)
				#
			#
		#
	#

	def _apply_sub_entries_join_condition(self, db_query, context = None):
	#
		"""
Returns the modified SQLAlchemy database query with the "join" condition
applied.

:param context: Sub entries request context

:return: (object) SQLAlchemy database query
:since:  v0.1.00
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._apply_sub_entries_condition()- (#echo(__LINE__)#)", self, context = "pas_datalinker")

		_return = DataLinker._apply_sub_entries_join_condition(self, db_query, context)

		if (context == "DiscussTopic"):
		#
			_return = _return.join(_DbDiscussTopic,
			                       _DbDataLinker.id == _DbDiscussTopic.id
			                      )
		#

		return _return
	#

	def _apply_sub_entries_order_by_condition(self, db_query, context = None):
	#
		"""
Returns the modified SQLAlchemy database query with the "order by" condition
applied.

:param context: Sub entries request context

:return: (object) SQLAlchemy database query
:since:  v0.1.00
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._apply_sub_entries_order_by_condition()- (#echo(__LINE__)#)", self, context = "pas_datalinker")

		_return = db_query

		if (context == "DiscussTopic"):
		#
			sort_definition = self._get_db_sort_definition(context)
			if (sort_definition is not None): _return = sort_definition.apply(_DbDiscussTopic, db_query)
		#
		else: _return = DataLinker._apply_sub_entries_order_by_condition(self, db_query, context)

		return _return
	#

	def _get_data_attribute(self, attribute):
	#
		"""
Returns the data for the requested attribute.

:param attribute: Requested attribute

:return: (mixed) Value for the requested attribute; None if undefined
:since:  v0.1.00
		"""

		return (self.get_sub_entries_count()
		        if (attribute == "sub_entries") else
		        DataLinker._get_data_attribute(self, attribute)
		       )
	#

	def get_latest_timestamp(self):
	#
		"""
Returns the timestamp of the newest post of this or an subjacent list.

:return: (int) UNIX timestamp; -1 if no post exists
:since:  v0.1.00
		"""

		if (self.latest_timestamp is None): self._analyze_structure()
		return self.latest_timestamp
	#

	def get_latest_topic_id(self):
	#
		"""
Returns the topic ID of the newest post of this or an subjacent list.

:return: (str) Topic ID; None if post exists
:since:  v0.1.00
		"""

		if (self.latest_timestamp is None): self._analyze_structure()
		return self.latest_topic_id
	#

	def get_latest_author_id(self):
	#
		"""
Returns the author ID of the newest post of this or an subjacent list.

:return: (str) Author ID; None if post exists
:since:  v0.1.00
		"""

		if (self.latest_timestamp is None): self._analyze_structure()
		return self.latest_author_id
	#

	def get_latest_preview(self):
	#
		"""
Returns the preview of the newest post of this or an subjacent list.

:return: (str) Preview data; None if post exists
:since:  v0.1.00
		"""

		if (self.latest_timestamp is None): self._analyze_structure()
		return self.latest_preview
	#

	def get_sub_entries(self, offset = 0, limit = -1):
	#
		"""
Returns the child entries of this instance.

:param offset: SQLAlchemy query offset
:param limit: SQLAlchemy query limit

:return: (list) DataLinker children instances
:since:  v0.1.00
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.get_sub_entries({1:d}, {2:d})- (#echo(__LINE__)#)", self, offset, limit, context = "pas_datalinker")
		return DataLinker.get_sub_entries(self, offset, limit, exclude_identity = "DiscussTopic")
	#

	def get_sub_entries_count(self):
	#
		"""
Returns the number of child entries of this instance.

:return: (int) Number of child entries
:since:  v0.1.00
		"""

		return DataLinker.get_sub_entries_count(self, exclude_identity = "DiscussTopic")
	#

	def get_topics(self, offset = 0, limit = -1):
	#
		"""
Returns the children topics of this instance.

:param offset: SQLAlchemy query offset
:param limit: SQLAlchemy query limit

:return: (list) Topic children instances
:since:  v0.1.00
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.get_topics({1:d}, {2:d})- (#echo(__LINE__)#)", self, offset, limit, context = "pas_datalinker")
		return DataLinker.get_sub_entries(self, offset, limit, identity = "DiscussTopic")
	#

	get_topics_count = DataLinker._wrap_getter("topics")
	"""
Returns the number of topics of this instance.

:return: (int) Number of child topics
:since:  v0.1.00
	"""

	def get_total_posts_count(self):
	#
		"""
Returns the number of posts of this and all subjacent lists.

:return: (int) Number of posts
:since:  v0.1.00
		"""

		if (self.total_posts is None): self._analyze_structure()
		return self.total_posts
	#

	def get_total_topics_count(self):
	#
		"""
Returns the number of topics of this and all subjacent lists.

:return: (int) Number of topics
:since:  v0.1.00
		"""

		if (self.total_topics is None): self._analyze_structure()
		return self.total_topics
	#

	def _get_unknown_data_attribute(self, attribute):
	#
		"""
Returns the data for the requested attribute not defined for this instance.

:param attribute: Requested attribute

:return: (dict) Value for the requested attribute; None if undefined
:since:  v0.1.00
		"""

		if (attribute == "latest_author_id"): _return = self.get_latest_author_id()
		elif (attribute == "latest_preview"): _return = self.get_latest_preview()
		elif (attribute == "latest_timestamp"): _return = self.get_latest_timestamp()
		elif (attribute == "latest_topic_id"): _return = self.get_latest_topic_id()
		elif (attribute == "total_posts"): _return = self.get_total_posts_count()
		elif (attribute == "total_topics"): _return = self.get_total_topics_count()
		else: _return = DataLinker._get_unknown_data_attribute(self, attribute)

		return _return
	#

	def is_hybrid_list(self):
	#
		"""
A hybrid list can contain lists and topics.

:return: (bool) True if hybrid list
:since:  v0.1.00
		"""

		with self: return self.local.db_instance.hybrid_list
	#

	def set_data_attributes(self, **kwargs):
	#
		"""
Sets values given as keyword arguments to this method.

:since: v0.1.00
		"""

		self._ensure_thread_local_instance(_DbDiscussList)

		with self:
		#
			DataLinker.set_data_attributes(self, **kwargs)

			if ("id_subscription" in kwargs): self.local.db_instance.id_subscription = Binary.utf8(kwargs['id_subscription'])
			if ("hybrid_list" in kwargs): self.local.db_instance.hybrid_list = kwargs['hybrid_list']
			if ("owner_type" in kwargs): self.local.db_instance.owner_type = kwargs['owner_type']
			if ("description" in kwargs): self.local.db_instance.description = Binary.utf8(kwargs['description'])

			if ("topics" in kwargs):
			#
				if (kwargs['topics'] == "++"): self.local.db_instance.topics = self.local.db_instance.topics + 1
				elif (kwargs['topics'] == "--"):
				#
					if (self.local.db_instance.topics > 0): self.local.db_instance.topics = self.local.db_instance.topics - 1
				#
				else: self.local.db_instance.topics = kwargs['topics']
			#

			if ("posts" in kwargs):
			#
				if (kwargs['posts'] == "++"): self.local.db_instance.posts = self.local.db_instance.posts + 1
				elif (kwargs['posts'] == "--"):
				#
					if (self.local.db_instance.posts > 0): self.local.db_instance.posts = self.local.db_instance.posts - 1
				#
				else: self.local.db_instance.posts = kwargs['posts']
			#

			if ("last_id_topic" in kwargs): self.local.db_instance.last_id_topic = kwargs['last_id_topic']
			if ("last_id_author" in kwargs): self.local.db_instance.last_id_author = kwargs['last_id_author']
			if ("last_preview" in kwargs): self.local.db_instance.last_preview = Binary.utf8(kwargs['last_preview'])
			if ("locked" in kwargs): self.local.db_instance.locked = kwargs['locked']
			if ("guest_permission" in kwargs): self.local.db_instance.guest_permission = kwargs['guest_permission']
			if ("user_permission" in kwargs): self.local.db_instance.user_permission = kwargs['user_permission']
		#
	#

	@staticmethod
	def load_id_subscription(_id):
	#
		"""
Load List instance by its subscription ID.

:param _id: Subscription ID

:return: (object) List instance on success
:since:  v0.1.00
		"""

		if (_id is None): raise NothingMatchedException("List subscription ID is invalid")

		with Connection.get_instance() as connection: db_instance = connection.query(_DbDiscussList).filter(_DbDiscussList.id_subscription == _id).first()
		if (db_instance is None): raise NothingMatchedException("List subscription '{0}' is invalid".format(_id))
		return List(db_instance)
	#

	@staticmethod
	def load_id_subscription_list(_id, offset = 0, limit = -1):
	#
		"""
Load a list of matching List instances for the given subscription ID.

:param _id: Subscription ID
:param offset: SQLAlchemy query offset
:param limit: SQLAlchemy query limit

:return: (list) List of List instances on success
:since:  v0.1.00
		"""

		# TODO: load_list_... datalinker

		with Connection.get_instance() as connection:
		#
			db_query = connection.query(_DbDiscussList).filter(_DbDiscussList.id_subscription == _id)
			if (offset > 0): db_query = db_query.offset(offset)
			if (limit > 0): db_query = db_query.limit(limit)

			return List.buffered_iterator(_DbDiscussList, connection.execute(db_query))
		#
	#
#

##j## EOF