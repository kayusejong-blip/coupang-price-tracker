import sys
import os
import logging

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db, SessionLocal, Product
from backend.scheduler import check_prices

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run():
    """
    GitHub Actions용 일회성 실행 함수.
    DB 초기화 후 등록된 상품들의 가격을 스캔합니다.
    """
    logger.info("GitHub Actions: 쿠팡 가격 스캔 엔진 가동...")
    
    # 보안 설정 진단 (값은 가리고 유무만 확인)
    token = os.getenv("TELEGRAM_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    logger.info(f"진단: TELEGRAM_TOKEN 설정 여부 = {'O' if token else 'X'} (길이: {len(token)})")
    logger.info(f"진단: TELEGRAM_CHAT_ID 설정 여부 = {'O' if chat_id else 'X'} (길이: {len(chat_id)})")
    
    # DB 초기화 (테이블 생성 등)
    init_db()
    
    db = SessionLocal()
    try:
        count = db.query(Product).count()
        if count == 0:
            logger.warning("등록된 상품이 없습니다. 스캔을 건너뜁니다.")
            return
        
        logger.info(f"총 {count}개의 상품 스캔을 시작합니다.")
        # scheduler.py의 check_prices 함수 재사용
        check_prices()
        logger.info("모든 스캔 및 알림 전송 완료.")
        
    except Exception as e:
        logger.error(f"스캔 도중 오류 발생: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run()
