FROM ubuntu:latest

USER root

RUN apt-get update
RUN apt-get install -y openjdk-17-jdk
RUN apt-get install -y wget

RUN mkdir -p /opt/otp/home/wroclaw && mkdir -p /opt/otp/jar
RUN wget https://repo1.maven.org/maven2/org/opentripplanner/otp/2.3.0/otp-2.3.0-shaded.jar -O /opt/otp/jar/otp.jar

RUN wget https://transitfeeds.com/p/mpk-wroc-aw/663/20230607/download -O /opt/otp/home/wroclaw/mpk.gtfs.zip
RUN wget http://download.bbbike.org/osm/bbbike/Wroclaw/Wroclaw.osm.pbf -O /opt/otp/home/wroclaw/Wroclaw.osm.pbf

EXPOSE 8080
EXPOSE 8081

ENTRYPOINT [ "java", "-Xmx2G", "-jar", "/opt/otp/jar/otp.jar", "--build", "--serve", "/opt/otp/home/wroclaw"]
