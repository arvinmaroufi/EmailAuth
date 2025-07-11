from django.shortcuts import render
import random


def generate_verification_code():
    return ''.join(random.choices('0123456789', k=5))
