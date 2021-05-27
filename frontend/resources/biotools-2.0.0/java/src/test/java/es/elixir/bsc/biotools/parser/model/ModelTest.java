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

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.xml.bind.JAXBContext;
import javax.xml.bind.JAXBElement;
import javax.xml.bind.JAXBException;
import javax.xml.bind.SchemaOutputResolver;
import javax.xml.bind.Unmarshaller;
import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamReader;
import javax.xml.transform.Result;
import javax.xml.transform.stream.StreamResult;
import junit.framework.Assert;
import org.junit.Test;

/**
 *
 * @author Dmitry Repchevsky
 */

public class ModelTest {
    
//    @Test
//    public void test01() {
//        try {
//            JAXBContext ctx = JAXBContext.newInstance(Tools.class);
//            Unmarshaller u = ctx.createUnmarshaller();
//            
//            InputStream in = ModelTest.class.getClassLoader().getResourceAsStream("biotools-2.0-beta02.xml");
//            Assert.assertNotNull(in);
//            
//            XMLInputFactory f = XMLInputFactory.newFactory();
//            //f.setProperty(XMLInputFactory.IS_NAMESPACE_AWARE, Boolean.FALSE);
//            XMLStreamReader reader = f.createXMLStreamReader(in, "UTF-8");
//
//            JAXBElement<Tools> el = u.unmarshal(reader, Tools.class);
//        } catch (JAXBException | XMLStreamException ex ) {
//            Assert.fail(ex.getMessage());
//        }
//    }
    
    @Test
    public void test02() {
        try {
            JAXBContext ctx = JAXBContext.newInstance(Tools.class);
            ctx.generateSchema(new SchemaOutputResolver() {
                @Override
                public Result createOutput(String namespaceUri, String suggestedFileName) throws IOException {
                    //Result result = new StreamResult(new ByteArrayOutputStream());
                    Result result = new StreamResult(System.out);
                    result.setSystemId(namespaceUri);
                    return result;
                }
            });

        } catch (JAXBException ex ) {
            Assert.fail(ex.getMessage());
        } catch (IOException ex) {
            Logger.getLogger(ModelTest.class.getName()).log(Level.SEVERE, null, ex);
        }
    }
}
