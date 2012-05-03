#!/usr/bin/env python
"""Unittests for Protocol class"""

import unittest

from ConvergenceTestCase import ConvergenceTestCase

class TestProtocol(ConvergenceTestCase):
    """Tests for Convergence.Protocol class"""

    def test_default_notaries(self):
        """Test default_notaries()"""
        from Convergence import default_notaries
        notaries = default_notaries()
        self.assertEqual(len(notaries), 2)
        for notary in notaries:
            self.validate_Notary(notary)
      
if __name__ == "__main__":
    unittest.main()
