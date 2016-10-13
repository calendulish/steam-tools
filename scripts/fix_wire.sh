#!/bin/bash

sed 's/0.019999999552965164/0.02/g' -i ../ui/interface.xml
sed '/Steam login status/{n;s|pixbuf">steam|pixbuf">icons/steam|}' -i ../ui/interface.xml
sed '/SteamGifts login status/{n;s|pixbuf">steam|pixbuf">icons/steamgifts|}' -i ../ui/interface.xml
sed '/SteamCompanion login status/{n;s|pixbuf">steam|pixbuf">icons/steamcompanion|}' -i ../ui/interface.xml
