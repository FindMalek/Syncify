# Syncify

## Introduction:
Syncify is an open-source application, that lets you download Music, Albums, Playlist, ect... from Spotify, and converts Music to <MP3, AAC, FLAC, M4A, OPUS, VORBIS, WAV> files with full metadata and cover art. Albums and Playlists to (.m3a) files.
Syncify gives the ability to sync your Downloaded Music and Playlists across all of your devices.

### FFMPEG
Syncify relies on the open source FFmpeg library to convert and write metadata to the songs it downloads. Please make sure FFmpeg is installed on your computer and added to the System PATH. Follow the tutorial here.

### Playlists
If you want to use Syncify to download personal Spotify playlists, ensure their visibility is set to 'Public'. This is so Syncify can use the Spotify API to retrieve the song details from your playlist.

### Spotify Application
To use the Syncify Python module you will need your own Spotify developer application to access their API. To do this sign up [here](https://developer.spotify.com/). When you have made a new application take note of your client id and secret. You can pass the id and secret to Syncify:

#### Environment variables (recommended)
Now you need to add 2 environment variables to your system:

```SPOTIPY_CLIENT_ID```

```SPOTIPY_CLIENT_SECRET```

To find out how to do this find a tutorial online for your specific operating system. Once you have done this make sure to restart your shell.
