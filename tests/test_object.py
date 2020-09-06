# BOTLIB - the bot library
#
#

import types, unittest

from obj import Object, last, load, save

class Test_Object(unittest.TestCase):

    def test_empty(self):
        o = Object()
        self.assertTrue(not o) 

    def test_final(self):
        with self.assertRaises(TypeError):
            o = Object()
            o.last = "bla"
            o.last()

    def test_stamp(self):
        o = Object()
        save(o)
        self.assertTrue(o.__stamp__)

    def test_attribute(self):
        o = Object()
        o.bla = "test"
        p = save(o)
        oo = Object()
        load(oo, p)
        self.assertEqual(oo.bla, "test")

    def test_changeattr(self):
        o = Object()
        o.bla = "test"
        p = save(o)
        oo = Object()
        load(oo, p)
        oo.bla = "mekker"
        pp = save(oo)
        ooo = Object()
        load(ooo, pp)
        self.assertEqual(ooo.bla, "mekker")

    def test_last(self):
        o = Object()
        o.bla = "test"
        save(o)
        oo = Object()
        last(oo)
        self.assertEqual(oo.bla, "test")

    def test_lastest(self):
        o = Object()
        o.bla = "test"
        save(o)
        oo = Object()
        last(oo)
        oo.bla = "mekker"
        save(oo)
        ooo = Object()
        last(ooo)
        self.assertEqual(ooo.bla, "mekker")
