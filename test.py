import os
from llamaapi import LlamaAPI

# Replace 'Your_API_Token' with your actual API token
llama = LlamaAPI(os.environ.get("LLAMA_API_KEY"))

api_request_json = {
  "model": "llama3-70b",
  "messages": [
    {"role": "system", "content": "For the given text provide all concepts and relations between them in turtle format using Rdfs schema, schema.org and example.org for the enteties."},
    {"role": "user", "content": "Text: Two and a Half Men is an American television sitcom created by Chuck Lorre and Lee Aronsohn that originally aired on CBS from September 22, 2003, to February 19, 2015, with a total of twelve seasons consisting of 262 episodes. Originally starring Charlie Sheen in the lead role alongside Jon Cryer and Angus T. Jones, the series was about a hedonistic jingle writer, Charlie Harper, his uptight brother, Alan, and Alan's mischievous son, Jake. As Alan's marriage falls apart and divorce appears imminent, he and Jake move into Charlie's beachfront Malibu house and complicate Charlie's freewheeling life.In 2010, CBS and Warner Bros. Television reached a multiyear broadcasting agreement for the series, renewing it through at least the 2011–12 season.[1][2] In February 2011, however, CBS and Warner Bros. Television decided to end production for the rest of the eighth season after Sheen entered drug rehabilitation and made 'disparaging' comments about the series' creator and executive producer Chuck Lorre.[3] Sheen's contract was terminated the following month and he was written out of the show after it was confirmed that he was not returning to the series.[4] Ashton Kutcher was hired to replace him for Season 9 as Walden Schmidt, a billionaire who buys Charlie's house after his death. In April 2013, CBS renewed the series for an eleventh season after closing one-year deals with Kutcher and Cryer. Jones, who was attending college,[5] was relegated to recurring status, though he didn't make an appearance until the series finale.[6][7] In March 2014, CBS renewed the series for a twelfth season, which was later announced to be the series' last.[8][9] The season began airing in October 2014 and concluded in February 2015 with the 40-minute series finale 'Of Course He's Dead'.[10][11] The success of the series led to it being the third-highest revenue-generating program for 2012, earning $3.24 million an episode.[12]"},
  ]
}

# Make your request and handle the response
response = llama.run(api_request_json)

answer_content = response.json()["choices"][0]["message"]["content"]

print(answer_content)

