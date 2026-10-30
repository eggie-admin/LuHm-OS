package art.eggiebagelface.luhmos.web3;

import java.io.InputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.security.MessageDigest;
import java.util.Enumeration;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;
import java.util.zip.CRC32;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

/** Read-only Java 17 check for Python DEV ZIP artifacts; does not extract or install. */
public final class ZipInteropInspector {
    private static final int MAX_FILES=96;
    private static final long MAX_BYTES=6_000_000L;
    private static final long MAX_ENTRY=2_000_000L;
    private static final String ROOT="luhmos-dev/";
    private ZipInteropInspector(){}

    private static boolean safeName(String name) {
        if (name==null || !name.startsWith(ROOT) || name.length()>240 ||
            name.indexOf('\\')>=0 || name.indexOf('\0')>=0 ||
            name.contains("//") || name.endsWith("/")) return false;
        String[] parts=name.split("/",-1);
        if (parts.length<2) return false;
        for (String part:parts) {
            if (part.isEmpty() || part.equals(".") || part.equals("..") ||
                part.endsWith(".") || part.endsWith(" ")) return false;
            String stem=part.split("\\.",2)[0].toUpperCase(Locale.ROOT);
            if (stem.equals("CON") || stem.equals("PRN") || stem.equals("AUX") ||
                stem.equals("NUL") || stem.matches("(COM|LPT)[1-9]")) return false;
        }
        if (!name.matches("[A-Za-z0-9._/-]+")) return false;
        return true;
    }

    private static String sha256(File path) throws Exception {
        MessageDigest md=MessageDigest.getInstance("SHA-256");
        try(InputStream in=new FileInputStream(path)) {
            byte[] buffer=new byte[65536];
            int n;
            while((n=in.read(buffer))>=0) if(n>0) md.update(buffer,0,n);
        }
        StringBuilder hex=new StringBuilder(64);
        for(byte b:md.digest()){
            hex.append(Character.forDigit((b>>>4)&15,16));
            hex.append(Character.forDigit(b&15,16));
        }
        return hex.toString();
    }

    public static int verify(File archive,String expectedDigest,int expectedEntries) throws Exception {
        if(expectedDigest==null || !expectedDigest.matches("[a-f0-9]{64}") ||
            expectedEntries<1 || expectedEntries>MAX_FILES) throw new IOException("INVALID_RECEIPT_INPUT");
        if(!archive.isFile() || !archive.getCanonicalPath().equals(archive.getAbsolutePath()) ||
            archive.length()<1 || archive.length()>MAX_BYTES) throw new IOException("ARCHIVE_SIZE_OR_PATH");
        if(!sha256(archive).equals(expectedDigest))throw new IOException("ARCHIVE_SHA256_MISMATCH");
        int count=0;
        long total=0;
        Set<String> seen=new HashSet<>();
        try(ZipFile zip=new ZipFile(archive)) {
            Enumeration<? extends ZipEntry> members=zip.entries();
            byte[] buffer=new byte[65536];
            while(members.hasMoreElements()) {
                ZipEntry item=members.nextElement();
                if(!safeName(item.getName()) || item.isDirectory() ||
                    !seen.add(item.getName().toLowerCase(Locale.ROOT)) || item.getMethod()!=ZipEntry.DEFLATED) {
                    throw new IOException("ZIP_MEMBER_NOT_ALLOWED");
                }
                long declared=item.getSize(), compressed=item.getCompressedSize();
                if(declared<0 || declared>MAX_ENTRY || compressed<0 ||
                   (declared>0 && compressed==0) ||
                   declared>200L*Math.max(1L,compressed)) throw new IOException("ZIP_MEMBER_BOUNDS");
                CRC32 crc=new CRC32();
                long actual=0;
                try(InputStream in=zip.getInputStream(item)) {
                    int n;
                    while((n=in.read(buffer))>=0) {
                        if(n>0) {
                            actual+=n;
                            if(actual>MAX_ENTRY)throw new IOException("ZIP_STREAM_BOUNDS");
                            crc.update(buffer,0,n);
                        }
                    }
                }
                if(actual!=declared || crc.getValue()!=item.getCrc()) {
                    throw new IOException("ZIP_CRC_OR_SIZE_MISMATCH");
                }
                total+=actual;
                count++;
                if(total>MAX_BYTES || count>MAX_FILES) throw new IOException("ZIP_TOTAL_LIMIT");
            }
        }
        if(count!=expectedEntries)throw new IOException("ZIP_ENTRY_COUNT_MISMATCH");
        return count;
    }

    public static void main(String[] args) throws Exception {
        if(args.length!=3)throw new IllegalArgumentException("ZIP_PATH EXPECTED_SHA256 ENTRY_COUNT");
        int count=verify(new File(args[0]),args[1],Integer.parseInt(args[2]));
        System.out.println("ZIP_JAVA17_SOURCE_GREEN entries="+count);
    }
}
