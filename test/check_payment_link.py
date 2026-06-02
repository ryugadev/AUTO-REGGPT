import asyncio
import inspect
from gpt_signup_hybrid.payment_link import get_checkout_url
from gpt_signup_hybrid.web.manager import LinkJob

def test_imports_and_signatures():
    print("Checking get_checkout_url signature...")
    sig = inspect.signature(get_checkout_url)
    print(f"Signature: {sig}")
    assert sig.return_annotation == tuple[str, str] or sig.return_annotation == 'tuple[str, str]', "Return type should be tuple[str, str]"
    
    print("Checking LinkJob dataclass fields...")
    job = LinkJob(id="test_id", email="test@example.com", password="pwd")
    assert hasattr(job, "promo_eligible"), "LinkJob should have promo_eligible field"
    assert job.promo_eligible is None, "promo_eligible default should be None"
    
    d = job.to_dict()
    assert "promo_eligible" in d, "to_dict should include promo_eligible key"
    print("LinkJob check passed!")

if __name__ == '__main__':
    test_imports_and_signatures()
