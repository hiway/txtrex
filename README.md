# txtrex

Publish a "blog" using DNS TXT records.

## Install:

- Clone the repo:
  ```bash
  $ git clone https://github.com/hiway/txtrex.git
  ```
- Install (pip):
  ```bash
  $ cd txtrex
  $ pip install -e .
  ```
- Alternative Install (setup.py):
  ```bash
  $ cd txtrex
  $ python setup.py install
  ```
  
## Run:

- Run with default port (`10053`), in repository root or ensure that 
  the `posts` directory exists in the current working directory:
  ```bash
  $ txtrex
  ```
- Run with specified port:
  ```bash
  $ txtrex --port 1053
  ```

## Examples:

- View latest post:
  ```bash
  $ dig @127.0.0.1 -p 10053 TXT +short rex.latest
  "# Hello"
  "This is a test."
  ```
- See recent posts:
  ```bash
  $ dig @127.0.0.1 -p 10053 TXT +short rex.index
  "Latest: rex.latest"
  "Recent:"
  "   rex.hello"
  "   rex.trying.something.silly"
  ```
- Read a specific post:
  ```bash
  $ dig @127.0.0.1 -p 10053 TXT +short rex.trying.something.silly
  "# Woohoo!"
  "This actually works?!"
  ```
- Comment on a post (comments are readable by admin only):  
  ```bash
  $ dig @127.0.0.1 -p 10053 TXT +short rex.trying.something.silly.comment.this.is.going.too.far
  "Posted:"
  "this is going too far"
  ```
- Search for a post:
  **[Not Implemented Yet]**
  ```bash
  $ dig @127.0.0.1 -p 10053 TXT +short rex.search.silly
  "# Search results for: silly"
  "rex.trying.something.silly # Woohoo!"
  ```

## Why?

I... needed something to break the coder's block, hence picked 
something I had not tried before: Twisted. Impressed with the
simplicity, decided to build something outrageous to get the
creative juices flowing. Here it is :)
