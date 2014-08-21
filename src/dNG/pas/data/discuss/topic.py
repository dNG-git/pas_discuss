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
from dNG.pas.database.lockable_mixin import LockableMixin
from dNG.pas.database.sort_definition import SortDefinition
from dNG.pas.database.instances.data_linker import DataLinker as _DbDataLinker
from dNG.pas.database.instances.discuss_post import DiscussPost as _DbDiscussPost
from dNG.pas.database.instances.discuss_topic import DiscussTopic as _DbDiscussTopic
from .list import List

class Topic(DataLinker, LockableMixin, OwnableLockableWriteMixin, SubscribableMixin):
#
	"""
"Topic" represents a discussion topic.

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
Constructor __init__(Topic)

:param db_instance: Encapsulated SQLAlchemy database instance

:since: v0.1.00
		"""

		DataLinker.__init__(self, db_instance)
		LockableMixin.__init__(self)
		OwnableLockableWriteMixin.__init__(self)
		SubscribableMixin.__init__(self)
	#

	def add_post(self, post, post_preview = None):
	#
		"""
Add the given child post.

:param post: DiscussPost instance
:param post_preview: Post preview

:since: v0.1.00
		"""

		# pylint: disable=protected-access

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.add_post()- (#echo(__LINE__)#)", self, context = "pas_datalinker")

		if (isinstance(post, DataLinker) and post.get_identity() == "DiscussPost"):
		#
			with self:
			#
				post_data = post.get_data_attributes("id", "author_id")

				if (post_data['id'] != self.local.db_instance.id):
				#
					post._get_db_instance().rel_main = self.local.db_instance

					self.set_data_attributes(time_sortable = time(),
					                         posts = "++",
					                         last_id_author = post_data['author_id'],
					                         last_preview = post_preview
					                        )
				#
			#
		#
	#

	def _get_default_sort_definition(self, context = None):
	#
		"""
Returns the default sort definition list.

:param context: Sort definition context

:return: (object) Sort definition
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._get_default_sort_definition({1})- (#echo(__LINE__)#)", self, context, context = "pas_datalinker")

		return (SortDefinition([ ( "position", SortDefinition.ASCENDING ),
		                         ( "time_sortable", SortDefinition.ASCENDING )
		                       ])
		        if (context == "DiscussPost") else
		        DataLinker._get_default_sort_definition(self, context)
		       )
	#

	def get_posts(self, offset = 0, limit = -1):
	#
		"""
Returns the children posts of this instance.

:param offset: SQLAlchemy query offset
:param limit: SQLAlchemy query limit

:return: (list) Post children instances
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.get_posts({1:d}, {2:d})- (#echo(__LINE__)#)", self, offset, limit, context = "pas_datalinker")

		with self:
		#
			db_query = self.local.connection.query(_DbDataLinker)

			db_query = db_query.filter(_DbDiscussTopic.id_main == self.local.db_instance.id,
			                           _DbDiscussTopic.identity == "DiscussPost"
			                          )

			db_query = List._db_apply_id_site_condition(db_query)

			db_query = self._apply_sub_entries_join_condition(db_query, "DiscussPost")
			db_query = self._apply_sub_entries_order_by_condition(db_query, "DiscussPost")
			if (offset > 0): db_query = db_query.offset(offset)
			if (limit > 0): db_query = db_query.limit(limit)

			return List.buffered_iterator(_DbDiscussPost, self.local.connection.execute(db_query), DataLinker)
		#
	#

	get_posts_count = DataLinker._wrap_getter("posts")
	"""
Returns the number of posts of this instance.

:return: (int) Number of child posts
:since:  v0.1.00
	"""

	def get_sub_entries(self, offset = 0, limit = -1):
	#
		"""
Returns the child entries of this instance.

:param offset: SQLAlchemy query offset
:param limit: SQLAlchemy query limit

:return: (list) DataLinker children instances
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.get_sub_entries({1:d}, {2:d})- (#echo(__LINE__)#)", self, offset, limit, context = "pas_datalinker")
		return DataLinker.get_sub_entries(self, offset, limit, exclude_identity = "DiscussPost")
	#

	def get_sub_entries_count(self):
	#
		"""
Returns the number of child entries of this instance.

:return: (int) Number of child entries
:since:  v0.1.00
		"""

		return DataLinker.get_sub_entries_count(self, exclude_identity = "DiscussPost")
	#

	def _insert(self):
	#
		"""
Insert the instance into the database.

:since: v0.1.00
		"""

		DataLinker._insert(self)

		with self.local.connection.no_autoflush:
		#
			if (self.local.db_instance.time_published == None): self.local.db_instance.time_published = int(time())

			data_missing = (self.is_data_attribute_none("owner_type", "guest_permission", "user_permission"))
			acl_missing = (len(self.local.db_instance.rel_acl) == 0)
			parent_object = (self.load_parent() if (data_missing or acl_missing) else None)

			if (data_missing and (isinstance(parent_object, List) or isinstance(parent_object, List))):
			#
				parent_data = parent_object.get_data_attributes("id_site", "owner_type", "guest_permission", "user_permission")

				if (self.local.db_instance.id_site == None and parent_data['id_site'] != None): self.local.db_instance.id_site = parent_data['id_site']
				if (self.local.db_instance.owner_type == None): self.local.db_instance.owner_type = parent_data['owner_type']
				if (self.local.db_instance.guest_permission == None): self.local.db_instance.guest_permission = parent_data['guest_permission']
				if (self.local.db_instance.user_permission == None): self.local.db_instance.user_permission = parent_data['user_permission']
			#

			# TODO: if (acl_missing and isinstance(parent_object, OwnableLockableWriteMixin)): self.data.acl_set_list(parent_object.data_acl_get_list())
		#
	#

	def set_data_attributes(self, **kwargs):
	#
		"""
Sets values given as keyword arguments to this method.

:since: v0.1.00
		"""

		self._ensure_thread_local_instance(_DbDiscussTopic)

		with self:
		#
			DataLinker.set_data_attributes(self, **kwargs)

			if ("id_subscription" in kwargs): self.local.db_instance.id_subscription = Binary.utf8(kwargs['id_subscription'])
			if ("owner_type" in kwargs): self.local.db_instance.owner_type = kwargs['owner_type']
			if ("author_id" in kwargs): self.local.db_instance.author_id = kwargs['author_id']
			if ("author_ip" in kwargs): self.local.db_instance.author_ip = kwargs['author_ip']

			if ("posts" in kwargs):
			#
				if (kwargs['posts'] == "++"): self.local.db_instance.posts = self.local.db_instance.posts + 1
				elif (kwargs['posts'] == "--"):
				#
					if (self.local.db_instance.posts > 0): self.local.db_instance.posts = self.local.db_instance.posts - 1
				#
				else: self.local.db_instance.posts = kwargs['posts']
			#

			if ("description" in kwargs): self.local.db_instance.description = Binary.utf8(kwargs['description'])
			if ("time_published" in kwargs): self.local.db_instance.time_published = int(kwargs['time_published'])
			if ("last_id_author" in kwargs): self.local.db_instance.last_id_author = kwargs['last_id_author']
			if ("last_preview" in kwargs): self.local.db_instance.last_preview = Binary.utf8(kwargs['last_preview'])
			if ("locked" in kwargs): self.local.db_instance.locked = kwargs['locked']
			if ("guest_permission" in kwargs): self.local.db_instance.guest_permission = kwargs['guest_permission']
			if ("user_permission" in kwargs): self.local.db_instance.user_permission = kwargs['user_permission']
		#
	#
#

##j## EOF