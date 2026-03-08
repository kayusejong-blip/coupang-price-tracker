from apscheduler.schedulers.background import BackgroundScheduler
from .database import SessionLocal, Product, PriceHistory
from .scraper import scrape_coupang
from .notifier import send_telegram_msg
import datetime
import logging

logger = logging.getLogger(__name__)

def check_prices():
    db = SessionLocal()
    try:
        products = db.query(Product).filter(Product.is_active == 1).all()
        total_count = len(products)
        change_count = 0
        
        logger.info(f"Checking prices for {total_count} products...")
        
        for product in products:
            logger.info(f"Checking price for: {product.name}")
            result = scrape_coupang(product.url)
            
            if result.get("success"):
                new_price = result["price"]
                old_price = product.current_price
                
                if new_price != old_price:
                    change_count += 1
                    # Price changed!
                    diff = new_price - old_price
                    direction = "📈 상승" if diff > 0 else "📉 하락"
                    
                    msg = (
                        f"🔔 <b>가격 변동 알림</b>\n\n"
                        f"📦 상품명: {product.name}\n"
                        f"💰 이전 가격: {old_price:,.0f}원\n"
                        f"✨ 현재 가격: {new_price:,.0f}원\n"
                        f"📊 변동폭: {direction} {abs(diff):,.0f}원\n\n"
                        f"🔗 <a href='{product.url}'>상품 보러가기</a>"
                    )
                    
                    # Update database
                    product.current_price = new_price
                    history = PriceHistory(product_id=product.id, price=new_price)
                    db.add(history)
                    db.commit()
                    
                    # Send notification
                    send_telegram_msg(msg, product.thumbnail)
                    logger.info(f"Price changed for {product.name}: {old_price} -> {new_price}")
                else:
                    logger.info(f"No price change for {product.name}")
            else:
                logger.error(f"Failed to check price for {product.url}: {result.get('error')}")

        # Send a summary message if no prices changed (to show the bot is alive)
        if change_count == 0 and total_count > 0:
            summary_msg = (
                f"✅ <b>정기 스캔 완료 보고</b>\n\n"
                f"📊 스캔 상품 수: {total_count}개\n"
                f"✨ 변동 사항: <b>없음</b>\n"
                f"🕒 확인 시간: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"봇이 정상 작동 중이며, 가격 변동이 감지되면 즉시 다시 보고드리겠습니다! 🫡"
            )
            send_telegram_msg(summary_msg)

    finally:
        db.close()

scheduler = BackgroundScheduler()

def start_scheduler():
    # Run every 30 minutes
    scheduler.add_job(check_prices, 'interval', minutes=30, id='price_checker')
    scheduler.start()
    logger.info("Scheduler started.")
