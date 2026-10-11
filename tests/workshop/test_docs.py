import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import check_docs

class DocumentationTest(unittest.TestCase):
    def test_published_markdown_links_and_encoding(self):
        files,errors=check_docs.check(ROOT)
        self.assertGreater(len(files),20)
        self.assertEqual(errors,[],'\n'.join(errors))

if __name__=='__main__':unittest.main()
