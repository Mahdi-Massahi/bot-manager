# import csv
# import unittest
# import os
#
# from nebixbm.command_center.notification.email import EmailSender
#
#
# class TestValidator(unittest.TestCase):
#     """Tests for EmailSender"""
#
#     def setUp(self):
#         """Sets up for each test"""
#         self.email_sender = EmailSender(
#             sender_email= "",
#             password= "",
#             smtp_host="smtp.gmail.com",
#         )
#
#     def test_send_email(self):
#         """Test to send an email"""
#         resp = self.email_sender.send_email(
#             "",
#             "First Email!",
#             "Hi,\n\nThis is the first notification from us!"+
#             "\nSincerely, Nebix Team",
#         )
#
#         self.assertTrue(resp)
