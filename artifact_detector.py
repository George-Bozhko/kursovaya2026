import re


class ArtifactDetector:

    def detect(self, text: str):

        hex_text = self._dewrap_hex(text)

        result = {
            "emails": self._find_emails(text),
            "ips": self._find_ips(text),
            "urls": self._find_urls(text),
            "passwords": self._find_passwords(text),
            "phones": self._find_phones(text),
            "md5": self._find_md5(hex_text),
            "sha1": self._find_sha1(hex_text),
            "sha256": self._find_sha256(hex_text),
            "domains": self._find_domains(text),

            "logins": self._find_logins(text),
            "mac_addresses": self._find_mac_addresses(text),
            "jwt_tokens": self._find_jwt_tokens(text),
            "api_keys": self._find_api_keys(text)
        }

        return result

    def _find_emails(self, text):

        pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

        return list(set(re.findall(pattern, text)))

    def _find_ips(self, text):

        pattern = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"

        return list(set(re.findall(pattern, text)))

    def _find_urls(self, text):

        pattern = r"https?://[^\s]+"

        return list(set(re.findall(pattern, text)))

    def _find_passwords(self, text):

        passwords = []

        patterns = [
            r"(?:пароль|password)[^:=\n]{0,30}[:=]\s*([^\s]+)"
        ]

        for pattern in patterns:

            matches = re.findall(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            passwords.extend(matches)

        return list(set(passwords))

    def _find_logins(self, text):

        logins = []

        patterns = [
            r"(?:логин|login|username|user)\s*[:=]\s*([^\s]+)"
        ]

        for pattern in patterns:

            matches = re.findall(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            logins.extend(matches)

        return list(set(logins))

    def _find_phones(self, text):

        pattern = (
            r"(?:\+7|8)"
            r"[\s\-]?"
            r"\(?\d{3}\)?"
            r"[\s\-]?"
            r"\d{3}"
            r"[\s\-]?"
            r"\d{2}"
            r"[\s\-]?"
            r"\d{2}"
        )

        return list(set(re.findall(pattern, text)))

    def _find_mac_addresses(self, text):

        pattern = (
            r"\b(?:[0-9A-Fa-f]{2}[:-]){5}"
            r"[0-9A-Fa-f]{2}\b"
        )

        return list(set(re.findall(pattern, text)))

    def _find_md5(self, text):

        pattern = r"\b[a-fA-F0-9]{32}\b"

        return list(set(re.findall(pattern, text)))

    def _find_sha1(self, text):

        pattern = r"\b[a-fA-F0-9]{40}\b"

        return list(set(re.findall(pattern, text)))

    def _find_sha256(self, text):

        pattern = r"\b[a-fA-F0-9]{64}\b"

        return list(set(re.findall(pattern, text)))

    def _find_jwt_tokens(self, text):

        pattern = (
            r"eyJ[a-zA-Z0-9_\-]+"
            r"\."
            r"[a-zA-Z0-9_\-]+"
            r"\."
            r"[a-zA-Z0-9_\-]+"
        )

        return list(set(re.findall(pattern, text)))

    def _find_api_keys(self, text):

        matches = []

        patterns = [

            r"sk-[A-Za-z0-9]{20,}",

            r"AIza[0-9A-Za-z\-_]{20,}",

            r"(?:api[_-]?key)\s*[:=]\s*([A-Za-z0-9_\-]{16,})"
        ]

        for pattern in patterns:

            found = re.findall(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            matches.extend(found)

        return list(set(matches))

    def _dewrap_hex(self, text):

        hash_lengths = {32, 40, 64}

        def join_if_hash(match):

            combined = match.group(1) + match.group(2)

            if len(combined) in hash_lengths:
                return combined

            return match.group(0)

        return re.sub(
            r"\b([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\b",
            join_if_hash,
            text
        )

    def _find_domains(self, text):

        pattern = r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b"

        domains = re.findall(pattern, text)

        filtered = []

        for domain in domains:

            if "@" not in domain:
                filtered.append(domain)

        return list(set(filtered))