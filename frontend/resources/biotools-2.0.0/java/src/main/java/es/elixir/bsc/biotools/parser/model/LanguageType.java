/**
 * *****************************************************************************
 * Copyright (C) 2016 ELIXIR ES, Spanish National Bioinformatics Institute (INB)
 * and Barcelona Supercomputing Center (BSC)
 *
 * Modifications to the initial code base are copyright of their respective
 * authors, or their employers as appropriate.
 * 
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301  USA
 *****************************************************************************
 */

package es.elixir.bsc.biotools.parser.model;

import javax.xml.bind.annotation.XmlEnum;
import javax.xml.bind.annotation.XmlEnumValue;

/**
 *
 * @author Dmitry Repchevsky
 */

@XmlEnum(EnumType.class)
public enum LanguageType {
    @XmlEnumValue("ActionScript") ACTION_SCRIPT("ActionScript"),
    @XmlEnumValue("Ada") ADA("Ada"),
    @XmlEnumValue("AppleScript") APPLE_SCRIPT("AppleScript"),
    @XmlEnumValue("Assembly language") ASSEMBLY_LANGUAGE("Assembly language"),
    @XmlEnumValue("AWK") AWK("AWK"),
    @XmlEnumValue("Bash") BASH("Bash"),
    @XmlEnumValue("C") C("C"),
    @XmlEnumValue("C#") CSharp("C#"),
    @XmlEnumValue("C++") CPP("C++"),
    @XmlEnumValue("COBOL") COBOL("COBOL"),
    @XmlEnumValue("ColdFusion") COLD_FUSION("ColdFusion"),
    @XmlEnumValue("CWL") CWL("CWL"),
    @XmlEnumValue("D") D("D"),
    @XmlEnumValue("Delphi") DELPHI("Delphi"),
    @XmlEnumValue("Dylan") DYLAN("Dylan"),
    @XmlEnumValue("Eiffel") EIFFEL("Eiffel"),
    @XmlEnumValue("Forth") FORTH("Forth"),
    @XmlEnumValue("Fortran") FORTRAN("Fortran"),
    @XmlEnumValue("Groovy") GROOVY("Groovy"),
    @XmlEnumValue("Haskell") HASKELL("Haskell"),
    @XmlEnumValue("Icarus") ICARUS("Icarus"),
    @XmlEnumValue("Java") JAVA("Java"),
    @XmlEnumValue("Javascript") JAVASCRIPT("Javascript"),
    @XmlEnumValue("JSP") JSP("JSP"),
    @XmlEnumValue("LabVIEW") LABVIEW("LabVIEW"),
    @XmlEnumValue("Lisp") LISP("Lisp"),
    @XmlEnumValue("Lua") LUA("Lua"),
    @XmlEnumValue("Maple") MAPLE("Maple"),
    @XmlEnumValue("Mathematica") MATHEMATICA("Mathematica"),
    @XmlEnumValue("MATLAB") MATLAB("MATLAB"),
    @XmlEnumValue("MLXTRAN") MLXTRAN("MLXTRAN"),
    @XmlEnumValue("NMTRAN") NMTRAN("NMTRAN"),
    @XmlEnumValue("Pascal") PASCAL("Pascal"),
    @XmlEnumValue("Perl") PERL("Perl"),
    @XmlEnumValue("PHP") PHP("PHP"),
    @XmlEnumValue("Prolog") PROLOG("Prolog"),
    @XmlEnumValue("PyMOL") PYMOL("PyMOL"),
    @XmlEnumValue("Python") PYTHON("Python"),
    @XmlEnumValue("R") R("R"),
    @XmlEnumValue("Racket") RACKET("Racket"),
    @XmlEnumValue("REXX") REXX("REXX"),
    @XmlEnumValue("Ruby") RUBY("Ruby"),
    @XmlEnumValue("SAS") SAS("SAS"),
    @XmlEnumValue("Scala") SCALA("Scala"),
    @XmlEnumValue("Scheme") SCHEME("Scheme"),
    @XmlEnumValue("Shell") SHELL("Shell"),
    @XmlEnumValue("Smalltalk") SMALLTALK("Smalltalk"),
    @XmlEnumValue("SQL") SQL("SQL"),
    @XmlEnumValue("Turing") TURING("Turing"),
    @XmlEnumValue("Verilog") VERILOG("Verilog"),
    @XmlEnumValue("VHDL") VHDL("VHDL"),
    @XmlEnumValue("Visual Basic") VISUAL_BASIC("Visual Basic"),
    @XmlEnumValue("Other") OTHER("Other");
    
    private final String value;
    
    private LanguageType(String value) {
        this.value = value;
    }
    
    @Override
    public String toString() {
        return value;
    }

    public static LanguageType fromValue(String value) {
        for (LanguageType type: LanguageType.values()) {
            if (type.value.equals(value)) {
                return type;
            }
        }
        throw new IllegalArgumentException(value);
    }
}
