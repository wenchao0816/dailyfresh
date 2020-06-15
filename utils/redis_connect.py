# coding=utf-8
from django_redis import get_redis_connection


class HashRedisConnect(object):
    def __init__(self, user, location='default'):
        self.conn = get_redis_connection(location)
        self.key = 'cart_key_%d' % user.id

    def set_cart(self, goods_id, num):
        self.conn.hset(self.key, goods_id, num)

    def get_cart(self, goods_id):
        return self.conn.hget(self.key, goods_id)

    def get_all_cart(self):
        return self.conn.hgetall(self.key)

    def del_cart(self, goods_id):
        self.conn.hdel(self.key, goods_id)


