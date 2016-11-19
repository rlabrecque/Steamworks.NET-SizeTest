using System;
using Steamworks;

namespace SteamworksNET_CallbackSizes {
	class Program {

		static void Main(string[] args) {
			if (!Packsize.Test()) {
				Console.WriteLine("You're using the wrong Steamworks.NET Assembly for this platform!");
				return;
			}
			
			CallbackSizes.Test();
		}
	}
}
