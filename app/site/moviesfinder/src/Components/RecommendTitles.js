import React, { Component } from "react";
import { bindAll } from "lodash";

class RecommendTitles extends Component {

  constructor() {
    super();
    this.state = {
      searchInput: "",
      foundTitles: [],
      selectedTitleId: "", 
      recommendedTitles: []
    };

    bindAll(
      this, 
      "searchTitles",
      "handleSearchChange",
      "handleTitleSelect",
      "recommendTitles"
    );
  }

  searchTitles(e) {

    let searchString = this.state.searchInput;

    fetch('https://vn1aniwdlj.execute-api.ap-southeast-2.amazonaws.com/live?search='+searchString, {
      "headers": {},
      "referrer": "",
      "referrerPolicy": "no-referrer-when-downgrade",
      "body": null,
      "method": "GET",
      "mode": "cors",
      "credentials": "omit"
    })
    .then(results => {return results.json();})
    .then(data => {
      this.setState({ 
        foundTitles: JSON.parse(data.titles).slice(0, 9), 
        selectedTitleId: "",
        recommendedTitles: []
      });
      return {
        foundTitles: this.state.foundTitles,
        selectedTitleId: this.state.selectedTitleId,
        recommendedTitles: this.state.recommendedTitles
      };
    });
  }

  handleSearchChange(e) {
    this.setState({
      searchInput: e.target.value
    });
  }

  handleTitleSelect(e) {
    this.setState({
      selectedTitleId: e.target.id
    });
    console.log("selected: ", e.target.id)
  }

  recommendTitles(e) {

    let reftitleid = this.state.selectedTitleId;

    fetch('https://vn1aniwdlj.execute-api.ap-southeast-2.amazonaws.com/live?recommendfortitle='+reftitleid, {
      "headers": {},
      "referrer": "",
      "referrerPolicy": "no-referrer-when-downgrade",
      "body": null,
      "method": "GET",
      "mode": "cors",
      "credentials": "omit"
    })
      .then(results => {
        return results.json();
      })
      .then(data => {
        this.setState({ recommendedTitles: JSON.parse(data.titles)});
        return {
          recommendedTitles: this.state.recommendedTitles
        };
      });
  }

  render() {
    
    let titleSelectHandler = this.handleTitleSelect
    let selectedTitleId = this.state.selectedTitleId

     let titlesElems = this.state.foundTitles.map(
       function(element, i){
         var titleId = element.titleid
         var title = element.title
        return (
          <div key={i}>
            <input 
              className={titleId === selectedTitleId ? "App-Button-Active" : "App-Button-Default"}
              id={titleId} 
              type="button" 
              value={title} 
              onClick={titleSelectHandler}
            />
            <br />
          </div>
        )
      }
    )

     let recommendationsElems = this.state.recommendedTitles.map(
       function(element, i){
         var titleId = element.titleid

         console.log("titleid: ", {titleId}.titleId)
         var title = element.title
         var url = "https://www.imdb.com/title/"+{titleId}.titleId
        return (
          <div key={i}>
            <a href={url}>{title}</a>
          </div>
        )
      }
    )
    
    return (
      <div id="recommend-titles">
          <h1>MoviesForMe.xyz</h1>
          <label>Search for a movie:  </label>
          <input
            type="text"
            id="search"
            name="search"
            placeholder="Type Title Here"
            onChange={this.handleSearchChange}
          />
          <input
            id="SearchButton"
            type="button"
            value="Search"
            onClick={this.searchTitles}
          />
          <br />
          <br />
          <label>Select Movie To Recommend On!</label>
          <br />
          <br />
          {titlesElems}
          <br />
          <br />
          <label>Recommend Movies</label>
          <br />
          <br />
          <input
            className={selectedTitleId === "" ? "hidden" : "nothidden"}
            id="RecommendButton"
            type="button"
            value="Recommend"
            onClick={this.recommendTitles}
          />
          <br />
          <br />
          {recommendationsElems}
          <br />
          <br />
          <br />
          <br />
      </div>
    );
  }
}

export default RecommendTitles;
