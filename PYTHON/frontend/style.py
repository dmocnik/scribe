from nicegui import ui

# Style pass
    # Serve the wallpaper background better (probably from local file)
    # Favicon
    # default style props

async def style():
    # Set the background image
    #bg_image = "https://images5.alphacoders.com/707/707888.jpg" # just in case :) 
    bg_image = "https://images7.alphacoders.com/568/568756.jpg"
    ui.query('body').style(f'''
                           background-image: url("{bg_image}");
                           background-size: cover;
                           background-repeat: no-repeat;
                           ''')
    
    # Set the colors
    ui.colors(primary='#8614d1')

    # Set the font
    ui.add_head_html('''
                    <style>
                        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap');
                     
                        html, body {
                            font-family: 'Inter', 'Roboto', sans-serif;
                        }
                    </style>
                    ''')
    
    # Default style for components
    # Input
    ui.input.default_props('outlined')

    # Select
    ui.select.default_props('outlined')

    # Card
    ui.card.default_style('background-color: #1d1d1dd9;')