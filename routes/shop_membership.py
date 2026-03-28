"""
Shop & Membership Routes - 商城与会员路由
"""
from flask import Blueprint, render_template, request, jsonify, session

shop_bp = Blueprint('shop', __name__)

@shop_bp.route('/membership')
def membership():
    """会员页面"""
    return render_template('membership.html')

@shop_bp.route('/shop')
def shop():
    """商城页面"""
    return render_template('shop.html')

@shop_bp.route('/api/shop/products')
def shop_products():
    """商品列表API"""
    # 返回示例数据
    products = [
        {'id': 1, 'name': '校徽徽章', 'price': 29.9, 'image': '/static/images/product1.jpg'},
        {'id': 2, 'name': '纪念T恤', 'price': 99, 'image': '/static/images/product2.jpg'},
    ]
    return jsonify({'success': True, 'products': products})

@shop_bp.route('/api/shop/products/<int:product_id>')
def shop_product_detail(product_id):
    """商品详情API"""
    return jsonify({
        'success': True,
        'product': {'id': product_id, 'name': f'Product {product_id}', 'price': 99}
    })

@shop_bp.route('/api/membership/levels')
def membership_levels():
    """会员等级API"""
    levels = [
        {'id': 'free', 'name': '免费会员', 'price': 0, 'features': ['浏览', '收藏']},
        {'id': 'basic', 'name': '基础会员', 'price': 99, 'features': ['浏览', '收藏', '评论']},
        {'id': 'pro', 'name': '专业会员', 'price': 299, 'features': ['浏览', '收藏', '评论', '下载', '导出']},
    ]
    return jsonify({'success': True, 'levels': levels})

@shop_bp.route('/api/membership/status')
def membership_status():
    """会员状态API"""
    if 'user_id' not in session:
        return jsonify({'success': True, 'level': 'free'})
    
    # 实际应从数据库查询
    return jsonify({'success': True, 'level': 'free', 'expire_date': None})

@shop_bp.route('/api/membership/upgrade', methods=['POST'])
def membership_upgrade():
    """升级会员API"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401
    
    data = request.get_json()
    level = data.get('level')
    
    # 实际应调用支付接口
    return jsonify({'success': True, 'message': f'Upgraded to {level}'})

@shop_bp.route('/api/payments/create', methods=['POST'])
def create_payment():
    """创建支付"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401
    
    data = request.get_json()
    amount = data.get('amount', 0)
    
    # 实际应调用支付接口
    return jsonify({'success': True, 'order_no': f'ORD{datetime.now().strftime("%Y%m%d%H%M%S")}'})

@shop_bp.route('/api/payments/<order_no>/status')
def payment_status(order_no):
    """支付状态"""
    return jsonify({'success': True, 'status': 'pending'})

def register_routes(app):
    """注册商城路由"""
    app.register_blueprint(shop_bp)

from datetime import datetime
