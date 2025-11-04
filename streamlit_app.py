import streamlit as st
import requests
import pandas as pd
from utils.met_api import search_met_artworks, get_artwork_details

def main():
    # 页面配置
    st.set_page_config(
        page_title="Explore Artworks with MET Museum API",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 应用标题
    st.title("Explore Artworks with MET Museum API")
    
    # 搜索部分
    st.header("Search for Artworks:")
    
    # 预设搜索按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌼 **flower**", use_container_width=True):
            st.session_state.search_term = "flower"
            st.session_state.trigger_search = True
    with col2:
        if st.button("🐦 **Chinese figure with bird**", use_container_width=True):
            st.session_state.search_term = "Chinese figure with bird"
            st.session_state.trigger_search = True
    
    # 自定义搜索
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        search_input = st.text_input(
            "Or enter your own search term:",
            placeholder="e.g., portrait, landscape, sculpture...",
            key="custom_search"
        )
    with search_col2:
        st.write("")  # 垂直间距
        custom_search_btn = st.button("Search", type="primary", use_container_width=True)
    
    # 确定搜索词
    search_term = None
    if 'search_term' in st.session_state and st.session_state.get('trigger_search', False):
        search_term = st.session_state.search_term
        st.session_state.trigger_search = False
    elif custom_search_btn and search_input:
        search_term = search_input
    elif search_input:
        search_term = search_input
    
    # 执行搜索并显示结果
    if search_term:
        display_artworks(search_term)
    
    # 页脚
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
    
    # 获取艺术品详情
    artworks = []
    progress_bar = st.progress(0)
    for i, artwork_id in enumerate(artwork_ids[:10]):  # 限制前10个结果
        artwork = get_artwork_details(artwork_id)
        if artwork and artwork.get('primaryImage'):
            artworks.append(artwork)
        progress_bar.progress((i + 1) / min(10, len(artwork_ids)))
    
    progress_bar.empty()
    
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
        
        with col2:
            # 显示信息
            st.write(f"**Title:** {artwork.get('title', 'Unknown Title')}")
            st.write(f"**Artist:** {artwork.get('artistDisplayName', 'Unknown Artist')}")
            st.write(f"**Year:** {artwork.get('objectDate', 'Unknown Date')}")
            
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
                if artwork.get('creditLine'):
                    st.write(f"**Credit Line:** {artwork['creditLine']}")
        
        st.markdown("---")


if __name__ == "__main__":
    main()
