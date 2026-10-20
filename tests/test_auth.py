import unittest

from pydantic import ValidationError

from app.auth import LoginRequest, RegisterRequest, hash_password, verify_password


class PasswordTests(unittest.TestCase):
    def test_password_hash_is_salted_and_verifies(self) -> None:
        first_hash = hash_password("correct horse battery staple")
        second_hash = hash_password("correct horse battery staple")

        self.assertNotEqual(first_hash, second_hash)
        self.assertTrue(verify_password("correct horse battery staple", first_hash))
        self.assertFalse(verify_password("incorrect password", first_hash))
        self.assertNotIn("correct horse battery staple", first_hash)

    def test_malformed_hash_is_rejected(self) -> None:
        self.assertFalse(verify_password("any password", "not-a-valid-hash"))


class AuthRequestTests(unittest.TestCase):
    def test_registration_normalizes_email_and_name(self) -> None:
        request = RegisterRequest(
            name="  Chatbot Member  ",
            email="  PERSON@Example.com ",
            password="a-long-and-secure-password",
        )

        self.assertEqual(request.name, "Chatbot Member")
        self.assertEqual(str(request.email), "person@example.com")

    def test_registration_rejects_short_password(self) -> None:
        with self.assertRaises(ValidationError):
            RegisterRequest(
                name="Member",
                email="person@example.com",
                password="short",
            )

    def test_login_normalizes_email(self) -> None:
        request = LoginRequest(
            email=" PERSON@Example.com ",
            password="any-password",
        )

        self.assertEqual(str(request.email), "person@example.com")


if __name__ == "__main__":
    unittest.main()