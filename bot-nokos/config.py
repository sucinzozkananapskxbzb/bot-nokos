import os

BOT_TOKEN = "8421697628:AAEp_YmBkr8fFfT3LIEXMX6ePieJUq3Vo8E"
ADMIN_IDS = [7591669325]  # Ganti dengan ID Telegram admin

# Konfigurasi Channel/Grup untuk OTP
OTP_CHANNEL_ID = "@FreeOtp7"  # Ganti dengan username channel
OTP_GROUP_ID = "--1002954697337"  # Ganti dengan ID grup (harus negatif)

# Konfigurasi Gacha
GACHA_SUCCESS_RATE = 0.05  # 5% success rate
COUNTRIES = {
    "US": {"name": "United States", "code": "+1"},
    "ID": {"name": "Indonesia", "code": "+62"},
    "MY": {"name": "Malaysia", "code": "+60"},
    "SG": {"name": "Singapore", "code": "+65"},
    "JP": {"name": "Japan", "code": "+81"},
    "KR": {"name": "South Korea", "code": "+82"},
    # 10 Negara tambahan dengan pengguna WhatsApp jarang
    "FI": {"name": "Finland", "code": "+358", "rare": True},
    "NO": {"name": "Norway", "code": "+47", "rare": True},
    "SE": {"name": "Sweden", "code": "+46", "rare": True},
    "DK": {"name": "Denmark", "code": "+45", "rare": True},
    "NZ": {"name": "New Zealand", "code": "+64", "rare": True},
    "IS": {"name": "Iceland", "code": "+354", "rare": True},
    "LU": {"name": "Luxembourg", "code": "+352", "rare": True},
    "EE": {"name": "Estonia", "code": "+372", "rare": True},
    "LT": {"name": "Lithuania", "code": "+370", "rare": True},
    "SI": {"name": "Slovenia", "code": "+386", "rare": True},
    # 10 Negara dengan penduduk sedikit (WhatsApp minoritas)
    "MC": {"name": "Monaco", "code": "+377", "small": True},
    "LI": {"name": "Liechtenstein", "code": "+423", "small": True},
    "SM": {"name": "San Marino", "code": "+378", "small": True},
    "VA": {"name": "Vatican City", "code": "+379", "small": True},
    "AD": {"name": "Andorra", "code": "+376", "small": True},
    "MT": {"name": "Malta", "code": "+356", "small": True},
    "CY": {"name": "Cyprus", "code": "+357", "small": True},
    "BH": {"name": "Bahrain", "code": "+973", "small": True},
    "QA": {"name": "Qatar", "code": "+974", "small": True},
    "BN": {"name": "Brunei", "code": "+673", "small": True}
}

# Format nomor untuk setiap negara
NUMBER_FORMATS = {
    "+1": "XXX-XXX-XXXX",  # US
    "+62": "XXX-XXXX-XXXX",  # Indonesia
    "+60": "XX-XXXX XXXX",  # Malaysia
    "+65": "XXXX-XXXX",  # Singapore
    "+81": "XX-XXXX-XXXX",  # Japan
    "+82": "XX-XXXX-XXXX",  # South Korea
    "+358": "XX-XXX-XXXX",  # Finland
    "+47": "XXX-XX-XXX",  # Norway
    "+46": "XX-XXX-XXXX",  # Sweden
    "+45": "XX-XX-XX-XX",  # Denmark
    "+64": "XX-XXX-XXXX",  # New Zealand
    "+354": "XXX-XXXX",  # Iceland
    "+352": "XXX-XXX-XXX",  # Luxembourg
    "+372": "XXXX-XXXX",  # Estonia
    "+370": "XXX-XXXXX",  # Lithuania
    "+386": "XX-XXX-XXX",  # Slovenia
    "+377": "XX-XXX-XXX",  # Monaco
    "+423": "XXX-XXXX",  # Liechtenstein
    "+378": "XXXX-XXXX",  # San Marino
    "+379": "XXX-XXXX",  # Vatican City
    "+376": "XXX-XXX",  # Andorra
    "+356": "XXXX-XXXX",  # Malta
    "+357": "XX-XXXXXX",  # Cyprus
    "+973": "XXXX-XXXX",  # Bahrain
    "+974": "XXXX-XXXX",  # Qatar
    "+673": "XXX-XXXX"  # Brunei
}