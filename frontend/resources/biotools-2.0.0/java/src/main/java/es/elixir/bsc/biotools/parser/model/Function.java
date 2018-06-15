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

import java.util.ArrayList;
import java.util.List;
import javax.xml.bind.annotation.XmlElement;
import javax.xml.bind.annotation.XmlSchemaType;
import javax.xml.bind.annotation.XmlType;
import javax.xml.bind.annotation.adapters.CollapsedStringAdapter;
import javax.xml.bind.annotation.adapters.XmlJavaTypeAdapter;

/**
 * 
 * @author Dmitry Repchevsky
 */

@XmlType(name = "", propOrder = {"operations",
                                 "inputs",
                                 "outputs",
                                 "comment"})
public class Function {

    private List<Operation> operations;
    protected List<Input> inputs;
    protected List<Output> outputs;
    protected String comment;

    @XmlElement(name = "operation", required = true)
    public List<Operation> getOperations() {
        if (operations == null) {
            operations = new ArrayList<>();
        }
        return operations;
    }

    @XmlElement(name = "input")
    public List<Input> getInputs() {
        if (inputs == null) {
            inputs = new ArrayList<>();
        }
        return inputs;
    }

    @XmlElement(name = "output")
    public List<Output> getOutputs() {
        if (outputs == null) {
            outputs = new ArrayList<>();
        }
        return outputs;
    }

    @XmlSchemaType(name = "textType", namespace = "http://bio.tools")
    @XmlJavaTypeAdapter(CollapsedStringAdapter.class)
    public String getComment() {
        return comment;
    }

    public void setComment(String comment) {
        this.comment = comment;
    }
}
