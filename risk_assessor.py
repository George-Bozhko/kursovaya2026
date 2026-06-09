class RiskAssessor:

    WEIGHTS = {
        "passwords": 5,
        "ips": 3,
        "sha256": 3,
        "logins": 3,

        "emails": 2,
        "phones": 2,
        "md5": 2,
        "sha1": 2,
        "mac_addresses": 2,

        "urls": 1,
        "domains": 1,

        "jwt_tokens": 8,
        "api_keys": 10
    }

    LABELS = {
        "passwords": "Пароли",
        "ips": "IP-адреса",
        "sha256": "SHA256-хеши",
        "logins": "Логины",

        "emails": "Email-адреса",
        "phones": "Телефоны",
        "md5": "MD5-хеши",
        "sha1": "SHA1-хеши",
        "mac_addresses": "MAC-адреса",

        "urls": "URL-ссылки",
        "domains": "Домены",

        "jwt_tokens": "JWT-токены",
        "api_keys": "API-ключи"
    }

    THRESHOLDS = [
        (35, "Критический"),
        (20, "Высокий"),
        (10, "Средний"),
        (0, "Низкий")
    ]

    def assess(self, artifacts):

        score = 0
        breakdown = []

        for key, weight in self.WEIGHTS.items():

            count = len(
                artifacts.get(key, [])
            )

            if count == 0:
                continue

            points = count * weight

            score += points

            breakdown.append({
                "type": self.LABELS.get(key, key),
                "count": count,
                "weight": weight,
                "points": points
            })

        # Корреляционный анализ

        if (
            artifacts.get("logins")
            and
            artifacts.get("passwords")
        ):

            score += 10

            breakdown.append({
                "type": "Связка логин + пароль",
                "count": 1,
                "weight": 10,
                "points": 10
            })

        if (
            artifacts.get("jwt_tokens")
            and
            artifacts.get("api_keys")
        ):

            score += 15

            breakdown.append({
                "type": "JWT + API-ключ",
                "count": 1,
                "weight": 15,
                "points": 15
            })

        breakdown.sort(
            key=lambda row: row["points"],
            reverse=True
        )

        return {
            "score": score,
            "level": self._level(score),
            "breakdown": breakdown
        }

    def _level(self, score):

        for threshold, level in self.THRESHOLDS:

            if score >= threshold:
                return level

        return "Низкий"

    @classmethod
    def weights_table(cls):

        return [
            {
                "type": cls.LABELS[key],
                "weight": weight
            }
            for key, weight in cls.WEIGHTS.items()
        ]

    @classmethod
    def thresholds_table(cls):

        rows = []

        thresholds = cls.THRESHOLDS

        for i, (low, level) in enumerate(thresholds):

            if i == 0:

                rng = f"{low} и выше"

            else:

                high = thresholds[i - 1][0] - 1

                rng = f"{low} – {high}"

            rows.append({
                "level": level,
                "range": rng
            })

        return rows