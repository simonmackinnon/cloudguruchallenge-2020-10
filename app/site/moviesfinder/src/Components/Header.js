import React, { Component } from "react";

class Header extends Component {

    render () {
        return (
            <div>
                <a href="/">
                    <img 
                        className="banner"
                        src="Banner.png"
                        alt="Movies For Me Banner" />
                </a>
            </div>
        );
    }

}

export default Header;