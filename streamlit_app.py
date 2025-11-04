import streamlit as st
import requests
import time

# 页面配置
st.set_page_config(
    page_title="Explore Artworks with MET Museum API",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API函数 - 直接定义在主文件中
@st.cache_data(ttl=3600)  # 缓存1小时
def search_met_artworks(query, limit=20):
    """搜索MET博物馆艺术品"""
    base_url = "https://collectionapi.metmuseum.org/public/collection/v1/search"
    params = {
        'q': query,
        'hasImages': True  # 只返回有图片的结果
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            object_ids = data.get('objectIDs', [])
            return object_ids[:limit]
        else:
            st.error(f"API请求失败: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"搜索时发生错误: {e}")
        return []

@st.cache_data(ttl=3600)  # 缓存1小时
def get_artwork_details(object_id):
    """获取艺术品详细信息"""
    url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"获取艺术品详情时发生错误: {e}")
        return None

def main():
    # 应用标题
    st.title("🎨 Explore Artworks with MET Museum API")
    
    # 搜索部分
    st.header("Search for Artworks:")
    
    # 预设搜索按钮 - 与图片内容完全匹配
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌼 **flower**", use_container_width=True, key="flower_btn"):
            st.session_state.search_term = "flower"
    with col2:
        if st.button("🐦 **Chinese figure with bird**", use_container_width=True, key="chinese_bird_btn"):
            st.session_state.search_term = "Chinese figure with bird"
    
    # 自定义搜索
    st.subheader("Or search for other artworks:")
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        custom_search = st.text_input(
            "Enter keywords:",
            placeholder="e.g., portrait, landscape, sculpture...",
            label_visibility="collapsed"
        )
    with search_col2:
        st.write("")  # 垂直间距
        custom_search_btn = st.button("Search", type="primary", use_container_width=True)
    
    # 确定搜索词
    search_term = None
    if 'search_term' in st.session_state:
        search_term = st.session_state.search_term
        # 清除session state以避免重复搜索
        del st.session_state.search_term
    elif custom_search_btn and custom_search:
        search_term = custom_search
    elif custom_search:
        search_term = custom_search
    
    # 执行搜索并显示结果
    if search_term:
        display_artworks(search_term)
    
    # 如果没有搜索，显示示例艺术品
    else:
        display_example_artworks()
    
    # 页脚 - 与图片内容完全匹配
    st.markdown("---")
    st.markdown("Presented by Prof. Jahwan Koo")
    st.markdown("©2024 ANASHE HUT")

def display_artworks(search_term):
    """显示搜索结果"""
    st.subheader(f"Search results for: '{search_term}'")
    
    # 搜索艺术品
    with st.spinner("Searching artworks..."):
        artwork_ids = search_met_artworks(search_term)
    
    if not artwork_ids:
        st.warning("No artworks found. Please try a different search term.")
        return
    
    # 显示艺术品数量
    st.info(f"Found {len(artwork_ids)} artworks")
    
    # 获取并显示前6个艺术品的详情
    artworks = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, artwork_id in enumerate(artwork_ids[:6]):  # 限制前6个结果
        status_text.text(f"Loading artwork {i+1}/6...")
        artwork = get_artwork_details(artwork_id)
        if artwork and artwork.get('primaryImage'):
            artworks.append(artwork)
        progress_bar.progress((i + 1) / 6)
        time.sleep(0.1)  # 避免API限制
    
    progress_bar.empty()
    status_text.empty()
    
    if not artworks:
        st.warning("No artworks with images found.")
        return
    
    # 显示艺术品
    for i, artwork in enumerate(artworks):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # 显示图片
            if artwork.get('primaryImage'):
                st.image(
                    artwork['primaryImage'],
                    use_column_width=True,
                    caption=artwork.get('title', 'Untitled')
                )
            else:
                st.info("🖼️ Image not available")
        
        with col2:
            # 显示信息
            title = artwork.get('title', 'Unknown Title')
            artist = artwork.get('artistDisplayName', 'Unknown Artist')
            year = artwork.get('objectDate', 'Unknown Date')
            
            st.write(f"**Title:** {title}")
            st.write(f"**Artist:** {artist}")
            st.write(f"**Year:** {year}")
            
            # 额外信息
            with st.expander("More Details"):
                if artwork.get('medium'):
                    st.write(f"**Medium:** {artwork['medium']}")
                if artwork.get('dimensions'):
                    st.write(f"**Dimensions:** {artwork['dimensions']}")
                if artwork.get('department'):
                    st.write(f"**Department:** {artwork['department']}")
                if artwork.get('culture'):
                    st.write(f"**Culture:** {artwork['culture']}")
                if artwork.get('classification'):
                    st.write(f"**Classification:** {artwork['classification']}")
                if artwork.get('creditLine'):
                    st.write(f"**Credit Line:** {artwork['creditLine']}")
        
        if i < len(artworks) - 1:  # 不在最后一个艺术品后显示分隔线
            st.markdown("---")

def display_example_artworks():
    """显示示例艺术品"""
    st.info("👆 Click one of the search buttons above or enter your own search term to explore artworks!")
    
    # 显示一些示例或说明
    st.markdown("""
    ### About this App
    
    This application allows you to explore artworks from The Metropolitan Museum of Art using their public API.
    
    **Features:**
    - Search thousands of artworks by keyword
    - View high-quality images
    - See detailed information about each artwork
    - Quick access to popular search terms
    
    **Try searching for:**
    - Renaissance
    - Impressionism  
    - Sculpture
    - Asian art
    - Modern art
    """)

if __name__ == "__main__":
    main()
