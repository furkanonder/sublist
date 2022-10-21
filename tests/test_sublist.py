import codecs
import unittest
from textwrap import dedent

from sublist import Codec, check_pattern


class TestSubList(unittest.TestCase):
    def test_decode(self):
        source = bytes("a = [x for x in range(20)]\nprint(a[0:3::3])", "utf-8")
        expected_result = dedent(
            """
        a = [x for x in range(20)]
        print([*[a[index:index + 3] for index in range(0, len(a), 3)][:3]])
        """
        ).strip()

        output, length = Codec().decode(source)
        self.assertEqual(output, expected_result)
        self.assertEqual(length, len(output))
        self.assertEqual(length, len(expected_result))

        self.assertEqual(b"hello world".decode("sublist"), "hello world")
        self.assertEqual(
            b'#coding: sublist\nprint("hello")'.decode("sublist"),
            "print('hello')",
        )

        self.assertRaises(
            UnicodeError, Codec().decode, input=b"python", errors="ignore"
        )
        self.assertEqual(b"test".decode("sublist", errors="strict"), "test")

    def test_encode(self):
        source = "a = [x for x in range(20)]\nprint(a[1:2::3])"
        expected_result = dedent(
            """
        a = [x for x in range(20)]
        print([*[a[index:index + 2] for index in range(1, len(a), 2)][:3]])
        """
        ).strip()

        output, length = Codec().encode(source)
        self.assertEqual(output, bytes(expected_result, "utf-8"))
        self.assertEqual(length, len(output))
        self.assertEqual(length, len(expected_result))

        self.assertEqual("hello world".encode("sublist"), b"hello world")
        self.assertEqual(
            '#coding: sublist\nprint("hello")'.encode("sublist"),
            b"print('hello')",
        )

        self.assertRaises(
            UnicodeError, Codec().encode, input="pep", errors="ignore"
        )
        self.assertEqual("test".encode("sublist", errors="strict"), b"test")

    def test_pattern(self):
        self.assertTrue(check_pattern("[0:4::1]"))
        self.assertFalse(check_pattern("[2:31:1]"))
        self.assertTrue(check_pattern("[2    : 3::2]"))
        self.assertTrue(check_pattern("[   1  : 3 :: 2]"))

    def test_incremental_encoder(self):
        incremental_encoder = codecs.getincrementalencoder("sublist")
        self.assertEqual(
            incremental_encoder().encode(input="a[0:4::1]"),
            b"[*[a[index:index + 4] for index in range(0, len(a), 4)][:1]]",
        )

    def test_incremental_decoder(self):
        incremental_decoder = codecs.getincrementaldecoder("sublist")
        self.assertEqual(
            incremental_decoder().decode(input=b"a[0:4::1]"),
            "\n[*[a[index:index + 4] for index in range(0, len(a), 4)][:1]]",
        )
