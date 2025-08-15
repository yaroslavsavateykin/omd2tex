class Global:
    REFERENCE_DICT = {}
    MIN_HEADLINE_LEVEL = 100

    @classmethod
    def clear(cls):
        cls.REFERENCE_DICT = {}
        cls.MIN_HEADLINE_LEVEL = 100

    @classmethod
    def check(cls):
        print("\nGlobal")
        print(f"REFERENCE_DICT = {cls.REFERENCE_DICT}")
        print(f"MIN_HEADLINE_LEVEL = {cls.MIN_HEADLINE_LEVEL}")
