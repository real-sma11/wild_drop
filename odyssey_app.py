import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(page_title="WW ODYSSEY: WILD Airdrop Estimate", layout="wide")

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('wshards2.csv')
        # Convert Wallet column to lowercase for case-insensitive search
        df['Wallet_lower'] = df['Wallet'].str.lower()
        logger.info("Data loaded successfully")
        return df
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        st.error("Error loading data. Please check the CSV file.")
        return None

# Process wallet for search
def process_wallet(wallet):
    if len(wallet) >= 10:
        front = wallet[:6].lower()
        back = wallet[-4:].lower()
        # Use the same ellipsis character as in the CSV file
        return f"{front}…{back}"
    return wallet.lower()

# Main app
def main():
    st.title("WW ODYSSEY: WILD Airdrop Estimate")
    st.subheader("This may estimate high")
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Sidebar
    with st.sidebar:
        st.header("Search Wallet")
        wallet_input = st.text_input("Enter your wallet address:")
        search_button = st.button("Search")
    
    # Initialize search result index and search results
    search_index = None
    name = None
    reward = None
    wshards = None
    
    # Process search if button is clicked
    if search_button and wallet_input:
        search_wallet = process_wallet(wallet_input)
        logger.info(f"Searching for wallet: {search_wallet}")
        
        # Search using the lowercase version of the wallet
        result = df[df['Wallet_lower'] == search_wallet]
        if not result.empty:
            name = result.iloc[0]['Name']
            reward = result.iloc[0]['Odyssey Drop']
            wshards = result.iloc[0]['wShards']
            search_index = result.index[0]  # Store the index for highlighting
    
    # Reward Distribution Graph
    st.markdown("### Reward Distribution")
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Create marker size and color arrays for highlighting
    marker_sizes = [6] * len(df)  # Default size
    marker_colors = df['Odyssey Drop']  # Default colors
    marker_line_width = [0] * len(df)  # Default line width
    marker_line_color = ['white'] * len(df)  # Default line color
    
    # If we found a search result, update its marker properties
    if search_index is not None:
        marker_sizes[search_index] = 12  # Larger marker for searched wallet
        marker_line_width[search_index] = 2  # Add border
        marker_line_color[search_index] = '#00ff00'  # Green border
    
    # Add Odyssey Drop trace
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['Odyssey Drop'],
            name='$WILD Drop',
            mode='markers',
            marker=dict(
                color=marker_colors,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(
                    title='$WILD Drop',
                    x=1.2  # Move colorbar further right
                ),
                size=marker_sizes,  # Use size array
                line=dict(
                    width=marker_line_width,  # Use line width array
                    color=marker_line_color  # Use line color array
                )
            ),
            hovertext=df.apply(lambda row: f"Rank: {row.name + 1}<br>Name: {row['Name']}<br>Wallet: {row['Wallet']}<br>$WILD Drop: {row['Odyssey Drop']:,.2f}<br>wShards: {row['wShards']:,.0f}", axis=1),
            hoverinfo='text'
        )
    )
    
    # Create marker properties for wShards
    wshard_sizes = [4] * len(df)  # Default size
    wshard_colors = ['rgba(255, 0, 0, 0.5)'] * len(df)  # Default color
    wshard_line_width = [0] * len(df)  # Default line width
    wshard_line_color = ['white'] * len(df)  # Default line color
    
    # If we found a search result, update its marker properties
    if search_index is not None:
        wshard_sizes[search_index] = 8  # Larger marker for searched wallet
        wshard_colors[search_index] = 'rgba(255, 0, 0, 0.8)'  # More opaque red
        wshard_line_width[search_index] = 2  # Add border
        wshard_line_color[search_index] = '#00ff00'  # Green border
    
    # Add wShards trace with offset x values
    fig.add_trace(
        go.Scatter(
            x=df.index + 25,  # Smaller offset for x values
            y=df['wShards'],
            name='wShards',
            mode='markers',
            marker=dict(
                color=wshard_colors,
                size=wshard_sizes,
                line=dict(
                    width=wshard_line_width,
                    color=wshard_line_color
                )
            ),
            yaxis='y2',
            hoverinfo='text',
            hovertext=df.apply(lambda row: f"Rank: {row.name + 1}<br>wShards: {row['wShards']:,.0f}", axis=1)
        )
    )
    
    # Update layout
    fig.update_layout(
        title='Distribution of Rewards (Log Scale)',
        xaxis_title="Rank",
        yaxis_title="$WILD Drop",
        showlegend=True,
        height=600,
        # Add more margin on right side for labels
        margin=dict(r=200, t=100, b=50, l=50),
        plot_bgcolor='rgb(17, 17, 17)',  # Dark background to match
        paper_bgcolor='rgb(17, 17, 17)',  # Dark background to match
        font=dict(color='white'),  # White text
        yaxis=dict(
            type='log',
            range=[np.log10(1), np.log10(df['Odyssey Drop'].max())],
            tickformat=".0f",
            title_standoff=20,  # Add space between title and axis
            gridcolor='rgba(128, 128, 128, 0.2)',  # Subtle grid lines
            color='white'  # White axis text
        ),
        yaxis2=dict(
            title="wShards",
            overlaying="y",
            side="right",
            type='log',
            range=[np.log10(1), np.log10(df['wShards'].max())],
            tickformat=".0f",
            title_standoff=60,  # Add more space between title and axis
            gridcolor='rgba(128, 128, 128, 0.2)',  # Subtle grid lines
            color='white'  # White axis text
        ),
        xaxis=dict(
            gridcolor='rgba(128, 128, 128, 0.2)',  # Subtle grid lines
            color='white'  # White axis text
        ),
        legend=dict(
            yanchor="bottom",
            y=1.02,  # Position above the plot
            xanchor="center",
            x=0.5,  # Center horizontally
            bgcolor='rgb(17, 17, 17)',  # Dark background to match
            bordercolor='white',  # White border
            font=dict(color='white'),  # White text
            orientation="h"  # Horizontal layout
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Your Estimated Rewards Section
    st.markdown("### Your Estimated Rewards")
    if search_button and wallet_input:
        if name is not None:  # We found a match
            # Display results on separate lines
            st.markdown(f"**Name:** {name}")
            st.markdown(f"**wShards:** {wshards:,.0f}")
            st.markdown(f'<p style="font-size: 24px;"><strong>$WILD Drop Estimate:</strong> {reward:,.2f}</p>', unsafe_allow_html=True)
            
            # Add vertical space and congratulatory message
            st.write("")
            st.write("")
            st.markdown("### Congratulations! 🎉")
            st.write("")
            st.write("Note: This is an estimate and may be higher than the actual amount you will receive. wShards were distributed based on WW NFT ownership. Total included in calculation is based on 5200 wallets, 60% proportional shared of 3 Million $WILD.")
        else:
            st.warning("No matching wallet found")

if __name__ == "__main__":
    main() 