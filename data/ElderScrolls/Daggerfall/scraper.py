from urllib.request import *
import time,os

base = "https://raw.githubusercontent.com/Interkarma/daggerfall-unity/57b758a1c3dce41f4379dd1934c2af43f12b5526/Assets/StreamingAssets/Quests/"

pages = ['$CUREVAM.txt', '$CUREWER.txt', '00B00Y00.txt', '10C00Y00.txt', '20C00Y00.txt', '30C00Y00.txt', '40C00Y00.txt', '50C00Y00.txt', '60C00Y00.txt', '70C00Y00.txt', '80C0XY00.txt', '90C00Y00.txt', 'A0C00Y00.txt', 'A0C00Y06.txt', 'A0C00Y07.txt', 'A0C00Y08.txt', 'A0C00Y10.txt', 'A0C00Y11.txt', 'A0C00Y12.txt', 'A0C00Y14.txt', 'A0C00Y15.txt', 'A0C00Y16.txt', 'A0C00Y17.txt', 'A0C01Y01.txt', 'A0C01Y03.txt', 'A0C01Y06.txt', 'A0C01Y09.txt', 'A0C01Y13.txt', 'A0C0XY04.txt', 'A0C10Y02.txt', 'A0C10Y05.txt', 'A0C41Y18.txt', 'B0B00Y00.txt', 'B0B00Y01.txt', 'B0B10Y04.txt', 'B0B20Y07.txt', 'B0B40Y08.txt', 'B0B40Y09.txt', 'B0B50Y11.txt', 'B0B60Y12.txt', 'B0B70Y14.txt', 'B0B70Y16.txt', 'B0B71Y03.txt', 'B0B80Y17.txt', 'B0B81Y02.txt', 'B0C00Y05.txt', 'B0C00Y06.txt', 'B0C00Y10.txt', 'B0C00Y13.txt', 'C0B00Y00.txt', 'C0B00Y01.txt', 'C0B00Y02.txt', 'C0B00Y03.txt', 'C0B00Y04.txt', 'C0B00Y14.txt', 'C0B10Y05.txt', 'C0B10Y06.txt', 'C0B10Y07.txt', 'C0B10Y15.txt', 'C0B20Y08.txt', 'C0B3XY09.txt', 'C0C00Y10.txt', 'C0C00Y11.txt', 'C0C00Y12.txt', 'C0C00Y13.txt', 'CUSTOM01.txt', 'D0B00Y00.txt', 'E0B00Y00.txt', 'F0B00Y00.txt', 'G0B00Y00.txt', 'H0B00Y00.txt', 'I0B00Y00.txt', 'J0B00Y00.txt', 'K0C00Y00.txt', 'K0C00Y02.txt', 'K0C00Y03.txt', 'K0C00Y04.txt', 'K0C00Y05.txt', 'K0C00Y06.txt', 'K0C00Y07.txt', 'K0C00Y08.txt', 'K0C00Y09.txt', 'K0C01Y00.txt', 'K0C01Y10.txt', 'K0C0XY01.txt', 'K0C30Y03.txt', 'L0A01L00.txt', 'L0B00Y00.txt', 'L0B00Y01.txt', 'L0B00Y02.txt', 'L0B00Y03.txt', 'L0B10Y01.txt', 'L0B10Y03.txt', 'L0B20Y02.txt', 'L0B30Y03.txt', 'L0B30Y09.txt', 'L0B40Y04.txt', 'L0B50Y11.txt', 'L0B60Y10.txt', 'M0B00Y00.txt', 'M0B00Y06.txt', 'M0B00Y07.txt', 'M0B00Y15.txt', 'M0B00Y16.txt', 'M0B00Y17.txt', 'M0B11Y18.txt', 'M0B1XY01.txt', 'M0B20Y02.txt', 'M0B21Y19.txt', 'M0B30Y03.txt', 'M0B30Y04.txt', 'M0B30Y08.txt', 'M0B40Y05.txt', 'M0B50Y09.txt', 'M0B60Y10.txt', 'M0C00Y11.txt', 'M0C00Y12.txt', 'M0C00Y13.txt', 'M0C00Y14.txt', 'N0B00Y04.txt', 'N0B00Y06.txt', 'N0B00Y08.txt', 'N0B00Y09.txt', 'N0B00Y16.txt', 'N0B00Y17.txt', 'N0B10Y01.txt', 'N0B10Y03.txt', 'N0B11Y18.txt', 'N0B20Y02.txt', 'N0B20Y05.txt', 'N0B21Y14.txt', 'N0B30Y15.txt', 'N0B40Y07.txt', 'N0C00Y10.txt', 'N0C00Y11.txt', 'N0C00Y12.txt', 'N0C00Y13.txt', 'O0A0AL00.txt', 'O0B00Y00.txt', 'O0B00Y01.txt', 'O0B00Y11.txt', 'O0B00Y12.txt', 'O0B10Y00.txt', 'O0B10Y03.txt', 'O0B10Y05.txt', 'O0B10Y06.txt', 'O0B10Y07.txt', 'O0B20Y02.txt', 'O0B2XY04.txt', 'O0B2XY08.txt', 'O0B2XY09.txt', 'O0B2XY10.txt', 'P0A01L00.txt', 'P0B00L01.txt', 'P0B00L03.txt', 'P0B00L04.txt', 'P0B00L06.txt', 'P0B01L02.txt', 'P0B10L07.txt', 'P0B10L08.txt', 'P0B10L10.txt', 'P0B20L09.txt', 'Q0C00Y01.txt', 'Q0C00Y03.txt', 'Q0C00Y04.txt', 'Q0C00Y06.txt', 'Q0C00Y07.txt', 'Q0C00Y08.txt', 'Q0C0XY02.txt', 'Q0C10Y00.txt', 'Q0C20Y02.txt', 'Q0C4XY04.txt', 'R0C10Y00.txt', 'R0C10Y01.txt', 'R0C10Y02.txt', 'R0C10Y04.txt', 'R0C10Y05.txt', 'R0C10Y06.txt', 'R0C10Y08.txt', 'R0C10Y09.txt', 'R0C10Y10.txt', 'R0C10Y11.txt', 'R0C10Y12.txt', 'R0C10Y13.txt', 'R0C10Y14.txt', 'R0C10Y15.txt', 'R0C10Y17.txt', 'R0C10Y18.txt', 'R0C10Y20.txt', 'R0C10Y21.txt', 'R0C11Y03.txt', 'R0C11Y16.txt', 'R0C11Y19.txt', 'R0C11Y26.txt', 'R0C11Y27.txt', 'R0C11Y28.txt', 'R0C20Y07.txt', 'R0C20Y22.txt', 'R0C30Y25.txt', 'R0C4XY23.txt', 'R0C60Y24.txt', 'S0000001.txt', 'S0000002.txt', 'S0000003.txt', 'S0000004.txt', 'S0000005.txt', 'S0000006.txt', 'S0000007.txt', 'S0000008.txt', 'S0000009.txt', 'S0000010.txt', 'S0000011.txt', 'S0000012.txt', 'S0000013.txt', 'S0000015.txt', 'S0000016.txt', 'S0000017.txt', 'S0000018.txt', 'S0000020.txt', 'S0000021.txt', 'S0000022.txt', 'S0000100.txt', 'S0000101.txt', 'S0000102.txt', 'S0000103.txt', 'S0000104.txt', 'S0000106.txt', 'S0000107.txt', 'S0000500.txt', 'S0000501.txt', 'S0000502.txt', 'S0000503.txt', 'S0000977.txt', 'S0000988.txt', 'S0000999.txt', 'T0C00Y00.txt', 'U0C00Y00.txt', 'V0C00Y00.txt', 'W0C00Y00.txt', 'X0C00Y00.txt', 'Y0C00Y00.txt', 'Z0C00Y00.txt', '_BRISIEN.txt']

for page in pages:
	# req = Request(
# 		base+page, 
# 		data=None, 
# 		headers={
# 			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
# 		}
# 	)
	fn = "raw/"+page
	if not os.path.isfile(fn):
		print("Downloading "+fn)
		dat = urlretrieve(base+page, fn)
		time.sleep(3)

#html = urlopen(req).read().decode('utf-8')
#o = open("raw/dialogueExport.txt",'w')
#o.write(html)
#o.close()
