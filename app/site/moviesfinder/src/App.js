import React, { Component } from 'react';
import ReactGA from 'react-ga';
import './App.css';
import RecommendTitles from './Components/RecommendTitles';

class App extends Component {

  handler(e) {
    e.preventDefault()
  }

  constructor(props){
    super(props);

    ReactGA.initialize('dsafdsf');
    ReactGA.pageview(window.location.pathname);
    this.handler = this.handler.bind(this)
  }


  render() {
    return (
      <div className="App">
        <RecommendTitles/>
      </div>
    );
  }
}

export default App;
