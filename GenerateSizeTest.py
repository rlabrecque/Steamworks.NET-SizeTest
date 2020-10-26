import os
import sys
from SteamworksParser import steamworksparser

g_SkippedStructs = (
    "PSNGameBootInviteResult_t",
    "PS3TrophiesInstalled_t",

    # We remap these ISteamController structs to ISteamInput
    "ControllerAnalogActionData_t",
    "ControllerDigitalActionData_t",
    "ControllerMotionData_t",

    # String formatting functions. We just use .ToString() instead.
    "SteamNetworkingIdentityRender",
    "SteamNetworkingIPAddrRender",
    "SteamNetworkingPOPIDRender",
)

g_SkippedFields = (
    "SteamIPAddress_t",
)


g_SpecialFieldTypes = {
    "SteamDatagramGameCoordinatorServerLogin": {
        "m_appData": "int8",
    },
}

def OutputCPP(callbacklines, structlines):
    with open("CPPHeader.txt" , "r") as header:
        CPPHeader = header.read()

    with open("Generated/Sizes.h", "w") as out:
        out.write(CPPHeader)
        for line in callbacklines:
            out.write(line + '\n')
        out.write('\tfs << ("=================================================\\n");\n')
        for line in structlines:
            out.write(line + '\n')
        out.write('\tfs << ("=================================================\\n");\n')
        out.write('\tfs.close();\n')
        out.write('}\n')  # Namespace

def OutputCSharp(callbacklines, structLines):
    with open("CSharpHeader.txt", "r") as header:
        CSharpHeader = header.read()

    with open("Generated/Sizes.cs", "w") as out:
        out.write(CSharpHeader)
        for line in callbacklines:
            out.write(line + '\n')
        out.write('\t\t\tlines.Add("=================================================");\n')
        for line in structLines:
            out.write(line + '\n')
        out.write('\t\t\tlines.Add("=================================================");\n')
        out.write("\t\t\tSystem.IO.File.WriteAllLines(path + filename, lines.ToArray());\n")
        out.write("\t\t}\n")
        out.write("\t}\n")
        out.write("}\n")

def ParseCSharp(struct):
    offsets = ''
    if struct.fields and struct.name not in g_SkippedFields:
        offsets = ' + ", Offsetof: "'
        for i, field in enumerate(struct.fields):
            if i > 0:
                 offsets += ' + ", "'

            fieldname = field.name

            fieldtype = g_SpecialFieldTypes.get(struct.name, {}).get(fieldname, field.type)

            if field.arraysize and fieldtype in ['const char *', 'char']:
                fieldname += '_'

            offsets += f' + Marshal.OffsetOf(typeof({struct.name}), "{fieldname}")'

    return '\t\t\tlines.Add("{0}, Sizeof: " + Marshal.SizeOf(typeof({0})){1});'.format(struct.name, offsets)

def ParseCpp(struct):
    offsets = '\tfs << "{0}, Sizeof: " << sizeof({0}) << '.format(struct.name)
    if len(struct.fields) > 0 and struct.name not in g_SkippedFields:
        offsets += ' ", Offsetof: " << '
        for i, field in enumerate(struct.fields):
            offsets += 'offsetof({0}, {1}) << '.format(struct.name, field.name)
            if i != len(struct.fields) - 1:
                offsets += '", " << '

    offsets += '"\\n";'
    return offsets

def main(parser):
    try:
        os.makedirs('Generated/')
    except OSError:
        pass

    csharpLines = []
    structLines = []
    cppcallbackLines = []
    cppcStructLines = []
    for f in parser.files:
        for callback in f.callbacks:
            if callback.name in g_SkippedStructs:
                continue
            csharpLines.append(ParseCSharp(callback))
            cppcallbackLines.append(ParseCpp(callback))

        for struct in f.structs:
            if struct.name in g_SkippedStructs:
                continue
            structLines.append(ParseCSharp(struct))
            cppcStructLines.append(ParseCpp(struct))

    OutputCSharp(csharpLines, structLines)
    OutputCPP(cppcallbackLines, cppcStructLines)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(steamworksparser.parse(sys.argv[1]))
    else:
        print("Usage: Steamworks.NET_CodeGen.py path/to/steamworks_header_folder/")

