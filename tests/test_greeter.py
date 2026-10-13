import json
import random
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path
from urllib.parse import unquote

from greeter import templates
from greeter.contacts import Contact, ContactBook
from greeter.service import draft
from greeter.sms import sms_link

EXAMPLE = Path(__file__).resolve().parent.parent / "contacts.example.json"


class SmsLinkTest(unittest.TestCase):
    def test_android_and_ios_formats(self):
        body = "엄마! 잘 지내? & 밥 먹었어?"
        android = sms_link("010-1234-5678", body)
        ios = sms_link("010-1234-5678", body, "ios")
        self.assertTrue(android.startswith("sms:01012345678?body="))
        self.assertTrue(ios.startswith("sms:01012345678&body="))
        self.assertEqual(unquote(android.split("body=", 1)[1]), body)
        self.assertNotIn("&", android.split("body=", 1)[1])


class TemplateTest(unittest.TestCase):
    def test_polite_and_casual(self):
        now = datetime(2026, 10, 13, 9)
        polite = Contact(id="g", name="할아버지", phone="1", relation="family", polite=True)
        casual = Contact(id="m", name="민수", phone="2", call_name="민수야")
        for seed in range(20):
            p = templates.generate(polite, now, random.Random(seed))
            c = templates.generate(casual, now, random.Random(seed))
            self.assertTrue(p.startswith("할아버지, "))
            self.assertTrue(any(e in p for e in ("요.", "요!", "요?")))
            self.assertTrue(c.startswith("민수야! "))
            self.assertNotIn("세요", c)

    def test_seasons(self):
        self.assertEqual(templates.season_of(10), "autumn")
        self.assertEqual(templates.season_of(1), "winter")
        self.assertEqual(templates.time_of(23), "night")


class ContactBookTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.contacts = self.tmp / "contacts.json"
        self.contacts.write_text(EXAMPLE.read_text(encoding="utf-8"), encoding="utf-8")
        self.state = self.tmp / "state.json"

    def test_mark_sent_persists_and_reorders(self):
        book = ContactBook(self.contacts, self.state)
        today = date(2026, 10, 13)
        self.assertTrue(all(c.is_due(today) for c in book.contacts.values()))
        book.mark_sent("mom", today)

        reloaded = ContactBook(self.contacts, self.state)
        mom = reloaded.get("mom")
        self.assertEqual(mom.last_sent, today)
        self.assertFalse(mom.is_due(today))
        self.assertEqual(reloaded.ordered(today)[-1].id, "mom")
        self.assertTrue(mom.is_due(date(2026, 10, 16)))

    def test_rejects_bad_relation(self):
        data = json.loads(self.contacts.read_text(encoding="utf-8"))
        data[0]["relation"] = "coworker"
        self.contacts.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(ValueError):
            ContactBook(self.contacts, self.state)


class ServiceTest(unittest.TestCase):
    def test_template_mode(self):
        c = Contact(id="m", name="엄마", phone="1", relation="family")
        d = draft(c, datetime(2026, 10, 13, 9), use_ai=False)
        self.assertEqual(d["source"], "template")
        self.assertTrue(d["text"].startswith("엄마! "))

    def test_falls_back_to_template_when_ai_unavailable(self):
        from unittest import mock
        from greeter import ai
        c = Contact(id="m", name="엄마", phone="1", relation="family")
        with mock.patch.object(ai, "_client", side_effect=ai.AIUnavailable("키 없음")):
            d = draft(c, datetime(2026, 10, 13, 9))
        self.assertEqual(d["source"], "template")
        self.assertEqual(d["warning"], "키 없음")


if __name__ == "__main__":
    unittest.main()
