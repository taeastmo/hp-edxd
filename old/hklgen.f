C   HKLGEN
C
C
      PROGRAM HKLGEN
      character*20 file
      character*20 bidon
      character*24 tempo
      logical qex
      COMMON /INOUT/LCA,LPR,LPRE,LT4,LT8,LFOR,LPUN
      COMMON /NUMB/N,N1,N2,N3,N4,N6,N7,NN,NN5,NA(3),NPAT,NTD,
     2 n8,n9,n10,n11,n12,n13
      COMMON /GEOM/DEGRAD,RADDEG
      PI=36000./3.14159265359
      DEGRAD=3.14159265359/180.0
      RADDEG=1.0/DEGRAD
      PRINT 1
1     format('  entry file (no extension) ??',$)
      READ 2,file
2     format(A20)
      lfile=len(file)
      do while (file(lfile:lfile).eq.' ')
	 lfile=lfile-1
      enddo
      LCA=20
      tempo=file(1:lfile)//'.dat'
      call open_read1(20,tempo)
      LPR=21
      tempo=file(1:lfile)//'.imp'
      inquire(file=tempo,exist=qex)
      if(qex.eq..FALSE.) go to 200
      call filedel(21,tempo)
200   call open_write1(21,tempo)
      CALL DATAIN(FILE)
      close(28,status='delete')
      close(32,status='delete')
      close(35,status='delete')
      PRINT 190
190   FORMAT('   Thanks for using HKLGEN')
      STOP
      END
*
      subroutine open_read1(unit,file)
      integer unit
      character*(*) file
      open (unit,file=file,status='old')
      return
      end
*
      subroutine open_read2(unit,file)
      integer unit
      character*(*) file
      open (unit,file=file,status='old',form='unformatted')
      return
      end
*
      subroutine open_write1(unit,file)
      integer unit
      character*(*) file
      open (unit,file=file,status='new')
      return
      end
*
      subroutine open_write2(unit,file)
      integer unit
      character*(*) file
      open (unit,file=file,status='scratch')
      return
      end
*
      subroutine filedel(unit,file)
      integer unit
      character*(*) file
      open (unit,file=file,status='old')
      close(unit,status='delete')
      return
      end
C	
C	Special Lazy version for creating hkl files
C
      SUBROUTINE LAZYR(SLABDA,OMEG,CELPRE,IGR,NP,ND,N1,N2)
      character*20 bidon
      character*20 file
      DIMENSION CELPRE(3,6),IGR(3,36)
      CALL PREDAT(FILE,SLABDA,OMEG,CELPRE,IGR,NP)
      CLOSE(28)
	CALL JAZY1(FILE,NP)
      close(29)
      close(30,status='delete')
      close(31,status='delete')
      CALL AHKL(ND,N1,N2)
      close(29,status='delete')
      close(36)
	RETURN
	END
C	
C	Program for preparing .dat files for LAZYR
C
      SUBROUTINE PREDAT(FILE,SLABDA,OMEG,CELPRE,IGR,NP)
      character*20 file
      character*24 temp
      logical qex
      character*20 bidon
      DIMENSION COMPND(19),CELPRE(3,6),IGR(3,36)
      IPR=28
      file='bidon'
      lfile=len(file)
      do while (file(lfile:lfile).eq.' ')
         lfile=lfile-1
      enddo
      temp=file(1:lfile)//'.dat'
      inquire(file=temp,exist=qex)
      if(qex.eq..FALSE.)go to 100
      call filedel(28,temp)
100   call open_write1(28,temp)
C      PRINT *,'TITLE CARD ?'
C      READ 44,(COMPND(I),I=1,19)
C 44   FORMAT(18A4,A2)
C-----T I T L E  CARD
      WRITE(IPR,45) (COMPND(I),I=1,19)
 45   FORMAT ('TITL  ',18A4,A2)
C      PRINT *,'Wavelenght and 2-theta end ?'
C      READ *,WL,TH
      WL=SLABDA
      TH=OMEG
      TL=0.
C-----C O N D I T  CARD                                                  
      WRITE(IPR,53)WL,TL,TH
 53   FORMAT ('CONDIT',8X,F6.4,2F5.0)
C      PRINT *,'A,B,C,ALPHA,BETA,GAMMA ?'
C      READ *,A,B,C,ALPHA,BETA,GAMMA
      A=CELPRE(NP,1)
      B=CELPRE(NP,2)
      C=CELPRE(NP,3)
      ALPHA=CELPRE(NP,4)
      BETA=CELPRE(NP,5)
      GAMMA=CELPRE(NP,6)
      IF(A.EQ.B)B=0.
      IF(ALPHA.EQ.90.)ALPHA=0.
      IF(BETA.EQ.90.)BETA=0.
      IF(GAMMA.EQ.90.)GAMMA=0.
C-----C E L L  CARD
      WRITE(IPR,49) A,B,C,ALPHA,BETA,GAMMA
 49   FORMAT ('CELL',9X,3F8.4,3F9.3)
C      PRINT *,'Space Group ?'
C      READ 50,(IGR(I),I=1,36)
C 50   FORMAT (36A1)
C-----S P C G R P  CARD
      WRITE(IPR,54) (IGR(NP,I),I=1,36)
 54   FORMAT ('SPCGRP',1X,36A1)
C-----A T O M  CARD
      WRITE(IPR,46)
 46   FORMAT ('ATOM   MN   10.1240  0.1760  0.2259  0.73')
C-----END  CARD
      WRITE(IPR,47)
 47   FORMAT ('END')
C-----FINISH  CARD
      WRITE(IPR,48)
 48   FORMAT ('FINISH')
	RETURN
	END
C
C      ERAPRE
C
      SUBROUTINE ERAPRE(file,npat,celpre,zero,SB,WDT,
     1CTHM,TMU,P1,Q1,R1,SLABDA,IGR,NDD,ND1,ND2)
      character*(*) file
      character*24 temp
      logical qex
	DIMENSION A(3,3),SLABDA(2),IGR(3,36)
      DIMENSION BCELL(3,3,3),P(3),Q(3),R(3),TEXT(20),CELPRE(3,6)
      DIMENSION NDD(3),ND1(3),ND2(3)
      COMMON II,NKEY,TEXT,NTEXT,KSTART,LPRE
      DATA NOX/3HNO./,BLANK/4H    /
C.....WHEN ANGLES IN 1/100TH DEGREES,FOLLOWING STATEMENT SHOULD READ:
C     RAD=3.14159265359/36000.
      RAD=3.14159265359/36000.
C.....READ AND PRINT TITLE
	LCA=20
	LPR=21
C
C.....READ CELL DIMENSIONS FOR EACH PATTERN
      I=1
      CALL CELL(A,I,CELPRE,LPR)
      DO 30 J=1,3
      DO 30 K=1,3
30    BCELL(I,K,J)=A(K,J)
      READ(LCA,*)OMEG
	OMEG=OMEG/2.
      N=0
	NP=1
      ND=NDD(NP)
      N1=ND1(NP)
      N2=ND2(NP)
      CALL LAZYR(SLABDA(1),OMEG,CELPRE,IGR,NP,ND,N1,N2)
      CLOSE(LPRE)
	RETURN

      END
      SUBROUTINE CELL(X,NP,CELPRE,LPR)
C     ***********************************************************
C     THE SUBROUTINE CELL READS EITHER DIRECT CELL PARAMETERS AND
C     CONVERTS THESE TO CELL CONSTANTS,WHICH ARE PLACED IN ARRAY X OR
C     READS CELL CONSTANTS AND PRINTS THE DIRECT CELL PARAMETERS.
C     ***********************************************************
C
C
      DIMENSION X(3,3),CELPRE(3,6)
C
C
      RAD=3.14159265359/180.
C	READ(LCA,*)(READIN(I),I=1,6)
      A=CELPRE(NP,1)
      B=CELPRE(NP,2)
      C=CELPRE(NP,3)
      D=CELPRE(NP,4)
      E=CELPRE(NP,5)
      F=CELPRE(NP,6)
      ISW=0
      IF(A.LT.1.)ISW=1
      IF(ISW.EQ.0)GOTO 10
      X(1,1)=A
      X(2,2)=B
      X(3,3)=C
      X(1,2)=F
      X(1,3)=E
      X(2,3)=D
      A=SQRT(A)
      B=SQRT(B)
      C=SQRT(C)
      COSA=D/(2.*B*C)
      COSB=E/(2.*A*C)
      COSC=F/(2.*A*B)
      GOTO 20
10    COSA=COS(RAD*D)
      COSB=COS(RAD*E)
      COSC=COS(RAD*F)
20    SINA=SQRT(1.-COSA*COSA)
      SINB=SQRT(1.-COSB*COSB)
      SINC=SQRT(1.-COSC*COSC)
      V=A*B*C*SQRT(1.-COSA*COSA-COSB*COSB-COSC*COSC+2.*COSA*COSB*COSC)
      AS=B*C*SINA/V
      BS=C*A*SINB/V
      CS=A*B*SINC/V
      COSAS=(COSB*COSC-COSA)/(SINB*SINC)
      COSBS=(COSC*COSA-COSB)/(SINC*SINA)
      COSCS=(COSA*COSB-COSC)/(SINA*SINB)
      IF(ISW.EQ.0)GOTO 30
      A=AS
      B=BS
      C=CS
      D=ATAN2(SQRT(1.-COSAS*COSAS),COSAS)/RAD
      E=ATAN2(SQRT(1.-COSBS*COSBS),COSBS)/RAD
      F=ATAN2(SQRT(1.-COSCS*COSCS),COSCS)/RAD
      GOTO 40
30    X(1,1)=AS*AS
      X(2,2)=BS*BS
      X(3,3)=CS*CS
      X(1,2)=2.*AS*BS*COSCS
      X(1,3)=2.*AS*CS*COSBS
      X(2,3)=2.*BS*CS*COSAS
40    WRITE(LPR,50)A,B,C,D,E,F
50    FORMAT(3H A=,F8.4,6X,2HB=,F8.4,6X,2HC=,F8.4/7H ALPHA=,F7.3,3X,
     2 5HBETA=,F7.3,4X,6HGAMMA=,F7.3)
      RETURN
      END
      SUBROUTINE DATAIN(FILE)
      CHARACTER*20 FILE
      character*24 tempo
      DIMENSION FC(8),DELFR(8),FA(8,10),FB(8,10),SLABDA(2)
	DIMENSION XL(210,14),LP(210,14),FLAG(210,14),IGR(3,36)
	DIMENSION RM(3,24,2,9),SM(3,24,3,3),T(3,24,3)
	DIMENSION F(6,21),S(6,21),G(3,200),RE(7),CELPRE(3,6)
      DIMENSION NDD(3),ND1(3),ND2(3),XRYZ(5),TEXT(20)
      LOGICAL FORCED,PUNCH,STAR,print,VERT,YES,ANGCOU
C
      DIMENSION IN(3,3),HH(3),IM(8),Z(3),TT(3)
C
      COMMON /LAZY/ ASS(3,24,3,3),ATS(3,24,3),IASYM(3),IABRA(3),NAG(3)
C
      COMMON /REFLN/ ARG,DELTA,DLABDA(2),EPS,FLOG,FLOG2,
     2    OMEGA,PI,SKEW,SLABDA,SLOG,W,XN,YCALC,YOBS
C
      COMMON /PREF/  IALFA,IOMEG,IORD1,IORD2,IPREV,ISTAP,ISS,
     1    KSTART,LIMO,LLL,NCD(200),NKEY,NO,NTEXT,NUM,NTYP(200),
     2    MEQ(200),MTYP(200)
C
      COMMON /SYMCEL/ ALL(3,3),AL(3,3,3),ATEXT(60),B(8),CELL(6),
     1    CELLN(3,6),FF(6),PH(3,3),
     2    TR(3,24),RCELL(6),RCELLN(3,6),
     3    VOLUME,VOL(3),PTEXT(3,4),AAL(3,6)
C
      COMMON /INOUT/LCA,LPR,LPRE,LT4,LT8,LFOR,LPUN
C
      COMMON /NUMB/N,N1,N2,N3,N4,N6,N7,NN,NN5,NA(3),NPAT,NTD,
     2 n8,n9,n10,n11,n12,n13
C
      COMMON /BFAC/ ITF,JTF(200),PRCP(3,6)
C
      COMMON /LOGIC/ FORCED,PUNCH,STAR,print,VERT,YES,ANGCOU
C
      COMMON /RELX/ RELAXB,RELAXC,RELAXS,RELAXH
C
      COMMON /INPUT/ NREAD,NPOINT,IRED,MODE,LINO,IDISML,READIN(6)
C
      COMMON /BACKGR/ IBACK,BAKGRD,WAVE1,WAVE3,VOLW3,VOLW(3),
     1    CROSS(8),BMAG(8),BAKG(3)
C
      DATA XRYZ(1),XRYZ(2),XRYZ(3),XRYZ(4),XRYZ(5)
     */2.28962,1.93597,1.54051,0.70926,0.556363/
C
C.....READ PROBLEM IDENTIFICATION
C
      READ(LCA,1) TEXT
C
C.....READ PROBLEM PARAMETERS
C
C
C.....WAVELENGTH
	READ(LCA,*) DLABDA(1)
C     print OF DATA
C
C.....PRINT PROGRAM HEADING
C
  190 CONTINUE
      WRITE(LPR,161) TEXT
C
C.....PRINT WAVELENGTH(S)
      SLABDA(1)=DLABDA(1)
  183 WRITE(LPR,21) DLABDA(1)
C
C.....READ SPACE GROUP FOR PHASE NP
C
      NP=1
      READ(LCA,479)(IGR(NP,IR),IR=1,36)
  479 FORMAT(36A1)
      WRITE(LPR,478)(IGR(NP,IR),IR=1,36)
  478 FORMAT('  SPACE GROUP : ',36A1)
C
C.....INPUT CELL DIMENSIONS
C
      NPAT=1
      DO 1210 NP=1,NPAT
      N2=N7+NP
      CALL DCELL(NP,CELPRE)
        DO 1200 I=1,3
        AAL(NP,I)=AL(NP,I,I)
 1200   XL(N2,I)=AL(NP,I,I)
      XL(N2,4)  =AL(NP,2,3)
      XL(N2,5)  =AL(NP,1,3)
      XL(N2,6) =AL(NP,1,2)
      AAL(NP,4)=2.*SQRT(AL(NP,1,1))*SQRT(AL(NP,2,2))    
      AAL(NP,5)=2.*SQRT(AL(NP,1,1))*SQRT(AL(NP,3,3))    
      AAL(NP,6)=2.*SQRT(AL(NP,2,2))*SQRT(AL(NP,3,3))    
 1210 CONTINUE
      CALL ERAPRE(file,npat,celpre,XL(N6,1),SB0,WDT,
     1CTHM,TMU,P1,Q1,R1,SLABDA,IGR,NDD,ND1,ND2)
C.....
    1 FORMAT(20A4)
   21 FORMAT('  WAVELENGTH',F8.5)
  161 FORMAT(1H ,20A4)
  221 RETURN
      END
      SUBROUTINE DCELL(NP,CELPRE)
C     ****************************************************
C     THIS SUBROUTINE READS THE CELL DIMENSIONS FROM THE INPUT STREAM,
      DIMENSION V(3),CELPRE(3,6)
      COMMON /REFLN/ARG,DELTA,DLABDA(2),EPS,FLOG,FLOG2,
     2 OMEGA,PI,SKEW,SLABDA,SLOG,W,XN,YCALC,YOBS
      COMMON /PREF/IALFA,IOMEG,IORD1,IORD2,IPREV,ISTAP,ISS,KSTART,LIMO,
     2 LLL,NCD(200),NKEY,NO,NTEXT,NUM,NTYP(200),MEQ(200),MTYP(200)
      COMMON /SYMCEL/ALL(3,3),AL(3,3,3),ATEXT(60),B(8),CELL(6),CELLN(3,
     2 6),FF(6),PH(3,3),
     3 TR(3,24),RCELL(6),RCELLN(3,6),VOLUME,VOL(3),PTEXT(3,4),AAL(3,6)
      COMMON /MINIM/COSARI(24),DERIV(200),H(24,3),HL(3,3),
     2 RSA(200,3),RSB(200,3),SA(200),SB(200),SINARI(24),
     3 SNEX(200),TEMP(200),TEXT(20)
      COMMON /INOUT/LCA,LPR,LPRE,LT4,LT8,LFOR,LPUN
      COMMON /BFAC/ITF,JTF(200),PRCP(3,6)
      COMMON /GEOM/DEGRAD,RADDEG
      COMMON /INPUT/NREAD,NPOINT,IRED,MODE,LINO,IDISML,READIN(6)
      EQUIVALENCE (VOL,V)
      DO 10 I=1,3
      DO 10 J=1,3
10    AL(NP,I,J)=0.0
      READ(LCA,*) (READIN(I),I=1,6)
      DO 11 I=1,6
11    CELPRE(NP,I)=READIN(I)
      IF(READIN(1)-1.0)20,60,60
20    ICELL=1
      DO 50 I=1,3
      AL(NP,I,I)=READIN(I)
      CALL PERM(I,J,K)
      IF(J-K)30,40,40
30    AL(NP,J,K)=READIN(I+3)
      GOTO 50
40    AL(NP,K,J)=READIN(I+3)
50    CONTINUE
      GOTO 140
60    ICELL=0
      DO 70 I=1,6
      CELLN(NP,I)=READIN(I)
70    CONTINUE
      DO 100 I=1,3
      L=I+3
      IF(CELLN(NP,L)-90.0)90,80,90
80    CELLN(NP,L)=0.0
      GOTO 100
90    CELLN(NP,L)=COS(DEGRAD*CELLN(NP,L))
100   CONTINUE
      CALL TRCL(CELLN,RCELLN,V,NP)
C     RCELL IS THE RECIPROCAL CELL CONSTANTS
      DO 130 I=1,3
      AL(NP,I,I)=RCELLN(NP,I)*RCELLN(NP,I)
      CALL PERM(I,J,K)
      IF(J-K)110,120,120
110   AL(NP,J,K)=2.0*RCELLN(NP,J)*RCELLN(NP,K)*RCELLN(NP,I+3)
      GOTO 130
120   AL(NP,K,J)=2.0*RCELLN(NP,J)*RCELLN(NP,K)*RCELLN(NP,I+3)
130   CONTINUE
      CALL BCONV(PRCP,AL,NP)
      RETURN
140   CALL REPCEL(RCELLN,AL,NP)
      CALL TRCL(RCELLN,CELLN,V,NP)
      V(NP)=1.0/V(NP)
      CALL BCONV(PRCP,AL,NP)
C     PRCP NOW CONTAINS THE COEFFICIENTS TO CONVERT BISO TO BIJ
C   1 FORMAT(6F10.4)
      RETURN
      END
      SUBROUTINE PERM(I,J,K)
C     PERMS USEFUL COMBINATIONS OF INTEGERS IN THE RANGE 1 TO 3
      IF(I-2)10,20,30
10    J=2
      K=3
      RETURN
20    J=3
      K=1
      RETURN
30    J=1
      K=2
      RETURN
      END
      SUBROUTINE TRCL(CELLN,RCELLN,V,NP)
C     TRANSFORMS REAL CELL TO RECIPROCAL OR VICE VERSA
C     INPUT CELL IS IN ARRAY CELL AS LENGTHS AND COSINES
      DIMENSION CELLN(3,6),RCELLN(3,6),V(3)
	DIMENSION SINA(3)
      ABC=1.0
      PROD=2.0
      V(NP)=-2.0
      DO 10 I=1,3
      L=I+3
      SINA(I)=1.0-CELLN(NP,L)**2
      V(NP)=V(NP)+SINA(I)
      SINA(I)=SQRT(SINA(I))
      PROD=PROD*CELLN(NP,L)
10    ABC=ABC*CELLN(NP,I)
      V(NP)=ABC*SQRT(V(NP)+PROD)
C      V IS CELL VOLUME
C     PUT INVERTED CELL INTO RCELL
      DO 20 I=1,3
      CALL PERM(I,J,K)
      RCELLN(NP,I)=CELLN(NP,J)*CELLN(NP,K)*SINA(I)/V(NP)
      L=I+3
20    RCELLN(NP,L)=(CELLN(NP,J+3)*CELLN(NP,K+3)-CELLN(NP,L))/(SINA(J)
     2 *SINA(K))
      RETURN
      END
      SUBROUTINE BCONV(RCELLN,AL,NP)
C     CALCULATES COEFFS TO CONVERT BISO TO BIJ
      DIMENSION RCELLN(3,6),AL(3,3,3)
      DO 30 I=1,3
      CALL PERM(I,J,K)
      RCELLN(NP,I)=AL(NP,I,I)*0.25
      IF(J-K)20,30,10
10    M=K
      K=J
      J=M
20    RCELLN(NP,7-I)=AL(NP,J,K)*0.125
30    CONTINUE
C     RCELLN NOW CONTAINS THE COEFFICIENTS TO CONVERT BISO TO BIJ
      RETURN
      END
      SUBROUTINE REPCEL(RCELLN,AL,NP)
C     OBTAINS RECIPROCAL CELL FROM METRIC TENSOR
      DIMENSION RCELLN(3,6),AL(3,3,3)
      DO 10 I=1,3
10    RCELLN(NP,I)=SQRT(AL(NP,I,I))
      DO 40 I=1,3
      CALL PERM(I,J,K)
      IF(J-K)30,40,20
20    M=K
      K=J
      J=M
30    RCELLN(NP,I+3)=0.5*AL(NP,J,K)/(RCELLN(NP,J)*RCELLN(NP,K))
40    CONTINUE
      RETURN
      END
	SUBROUTINE JAZY1(FILE,NP)
      character*20 file
      character*24 temp
      logical qex
	REAL N3,ISYMWL
	character*1 LBJ,IP,LJC,LJA,NORM,IANO,CEN,LJN,STIM(8),SDAT(9)
      DIMENSION CAR(9), IPOS(45),TSS(24,3),SS(24,3,3),
     1 RN(3), RD(3), S1(3), S2(3), S3(3), XYZ(3), COMPND(19), ELEMT(8),
     2 FNEUT(8), NA(8), DELFR(8), DELFI(8), IGR(45)
	DIMENSION FA(4,8),FB(4,8),FC(8),TS(3,24),FS(3,3,24),X(50,8),Y(50,
     * 8),Z(50,8),FOCCU(50,8),FMULT(50,8),IDE(50,8),BTEMP(50,8)
      INTEGER CAR,SS,SYMBR
      COMMON/BURC/TSS,SS
      COMMON /INPUT/ COMPND,ELEMT,FNEUT,A,B,C,ALPHA,BETA,
     1GAMMA,SYMSY,SYMBR,ISYMCE,NCOMPO,NA,SYMWL,WL,TL,TH,IMAGE,SYMLP,
     2AGUIN,BGUIN,DELFR,DELFI,NS,IBRAVL,NORM,IANO
      COMMON /UNITS/ ICR,IPR,ILU
      COMMON /POSIT/ RN,RD,S1,S2,S3,IGR
      COMMON /ANOMAL/ DEL1,DEL2
      COMMON /EXTI/ IHOO,IOKO,IOOL,IHKO,IHOL,IOKL,IHHL,LAUE,ITRIG
      COMMON /SLAS/ IP(8,3)
      COMMON /ND/ N3(20)
      COMMON /LAZY/ ASS(3,24,3,3),ATS(3,24,3),IASYM(3),IABRA(3),NAG(3)
      DATA CAR(1)/2HTI/,CAR(2)/2HAT/,CAR(3)/2HCE/,CAR(4)/2HLA/,CAR(5)/2H
     1SY/,CAR(6)/2HCO/,CAR(7)/2HSP/,CAR(8)/2HEN/,CAR(9)/2HFI/
      DATA BLNK/4HBBBB/,LBJ/1H /,LJC/'C'/,LJA/'A'/,LBB/'  '/
C-----SET LOGICAL UNIT NUMBERS
      ICR=32
      IPR=31
      ILU=29
      ILV=30
	IUN=33
	IDEUX=34
C      print 8576
C8576  format('  entry file (no extension) ??',$)
C      read 8577,file
C8577  format(A20)
      lfile=len(file)
      do while (file(lfile:lfile).eq.' ')
         lfile=lfile-1
      enddo
      temp=file(1:lfile)//'.dat'
      call open_read1(32,temp)
      temp=file(1:lfile)//'.imp'
      inquire(file=temp,exist=qex)
      if(qex.eq..FALSE.)go to 100
      call filedel(31,temp)
100   call open_write1(31,temp)
      inquire(file='LAZY.LAZ',exist=qex)
      if(qex.eq..FALSE.)go to 101
      call filedel(29,'LAZY.LAZ')
101     OPEN(UNIT=29,FILE='LAZY.LAZ',STATUS='NEW',FORM='UNFORMATTED')
      inquire(file='LAZY.JAZ',exist=qex)
      if(qex.eq..FALSE.)go to 102
      call filedel(30,'LAZY.JAZ')
102     OPEN(UNIT=30,FILE='LAZY.JAZ',STATUS='NEW')
C-----SET PROGRAM LIMITS
      LIMIT2=8
      LIMIT3=50
      LIMIT4=24
C-----
C-----READ INPUT FOR SEVERAL JOBS
C-----
      NJOB=0
      WRITE (IPR,38)SDAT,STIM
C-----READ FIRST CARD OF EACH SET
 1    READ (ICR,39) (IPOS(I),I=1,40)
C-----CHECK FOR FINISH CARD
      IF (IPOS(1).EQ.CAR(9)) GO TO 4
C-----COUNT NUMBER OF JOBS
      NJOB=NJOB+1
      WRITE (IPR,40) NJOB
      GO TO 3
C-----READ REMAINING DATA CARDS
 2    READ (ICR,39) (IPOS(I),I=1,40)
 3    WRITE (IPR,41) (IPOS(I),I=1,35)
C-----WRITE DATA CARDS TWICE ON DISK
      WRITE (ILV,391) (IPOS(I),I=1,40)
      WRITE (ILV,391) (IPOS(I),I=1,40)
C-----CHECK FOR END OF JOB
      IF (IPOS(1).NE.CAR(8)) GO TO 2
      WRITE (IPR,42)
      GO TO 1
 4    REWIND ILV
C	CALL CLOSE(ICR)
C-----
C-----START CALCULATION FOR NJOB JOBS
C-----
	WRITE(ILU)LFILE,FILE
      WRITE (ILU) NJOB
      DO 37 IJOB=1,NJOB
C-----
C-----SET DEFAULT VALUES
C-----
      ISYMWL=N3(14)
      SYMBR=N3(13)
      CEN=LJA
      NORM=LBJ
      WL=1.5418
      TL1=0.
      TH1=89.
      THG=45.
      IMAGE=2
      IANO=LBJ
C-----
C-----SET PARAMETERS BACK TO ORIGINAL VALUE
C-----
      LAUE=0
      ITRIG=3
      IHOO=1
      IOKO=1
      IOOL=1
      IHHL=1
      IHOL=1
      IOKL=1
      IHKO=1
      NCOMPO=1
      TH=TH1
      TL=TL1
      SYMWL=ISYMWL
      NS=0
      IGROUP=0
      ISYST=0
      ISYMCE=0
      A=0.
C-----SET ARRAYS BACK ZERO
      DO 5 I=1,36
 5    IGR(I)=LBB
      DO 6 I=1,LIMIT2
      ELEMT(I)=BLNK
      FNEUT(I)=0.
      DELFR(I)=0.
      DELFI(I)=0.
      FC(I)=0.
      DO 6 J=1,4
      FA(J,I)=0.
      FB(J,I)=0.
 6    NA(I)=0
      DO 7 I=1,3
      DO 7 J=1,3
      DO 7 K=1,LIMIT4
      TS(I,K)=0.
      FS(I,J,K)=0.
 7    CONTINUE
C-----TRIVIAL POSITION X,Y,Z
      FS(1,1,1)=1.
      FS(2,2,1)=1.
      FS(3,3,1)=1.
C-----LOOP OVER ALL DATA CARDS ON FILE ILV FOR ONE SET
 8    READ (ILV,43) INDF
C-----READ FIRST RECORD TO IDENTIFY FORMAT
      DO 9 J=1,8
      IF (INDF.NE.CAR(J)) GO TO 9
      M=J
      GO TO 10
 9    CONTINUE
      WRITE (IPR,44) INDF
      GO TO 35
C-----READ SECOND RECORD WITH CORRECT FORMAT
 10   GO TO (11,12,16,18,19,23,24,26), M
C-----T I T L E  CARD
 11   READ (ILV,45) (COMPND(I),I=1,19)
      GO TO 8
C-----A T O M  CARD
 12   READ (ILV,46) ELEMT1,IDE1,((IP(I,J),I=1,8),J=1,3),B1,FOCCU1
      CALL SLASH (XYZ(1),XYZ(2),XYZ(3))
      IF (FOCCU1.EQ.0.)FOCCU1=1.
      DO 13 I=1,NCOMPO
      NC=I
C-----ADD ATOM TO SAME ATOM KIND
      IF (ELEMT1.EQ.ELEMT(NC)) GO TO 14
 13   CONTINUE
C-----STORE ATOM AS NEW ATOMKIND
      IF (NA(1).EQ.0) GO TO 14
      NCOMPO=NCOMPO+1
      NC=NCOMPO
      IF (NCOMPO.LE.LIMIT2) GO TO 14
      WRITE (IPR,47) LIMIT2
      GO TO 35
 14   NA(NC)=NA(NC)+1
      I=NA(NC)
      IF (NA(NC).LE.LIMIT3) GO TO 15
      WRITE (IPR,48) NA(NC),ELEMT1,LIMIT3
      GO TO 35
 15   X(I,NC)=XYZ(1)
      Y(I,NC)=XYZ(2)
      Z(I,NC)=XYZ(3)
      ELEMT(NC)=ELEMT1
      IDE(I,NC)=IDE1
      FOCCU(I,NC)=FOCCU1
      BTEMP(I,NC)=B1
      GO TO 8
C-----C E L L  CARD
 16   READ (ILV,49) A,B,C,ALPHA,BETA,GAMMA
C-----CRYSTAL SYSTEM
      ISYSTM=2
      IF (B.NE.0.)GO TO 17
      IF (GAMMA.EQ.0.)ISYSTM=4
      IF (GAMMA.EQ.120.) ISYSTM=6
      IF (C.EQ.0.)ISYSTM=5
 17   IF (BETA.NE.0.)ISYSTM=1
      IF ((BETA.NE.0.).AND.(ALPHA.NE.0.)) ISYSTM=7
      GO TO 8
C-----L A T I C E  CARD
 18   READ (ILV,50) CEN,SYMBR
      IF (CEN.EQ.LJC) ISYMCE=1
      GO TO 8
C-----S Y M T R Y  CARD
 19   READ (ILV,51) (IGR(J),J=1,45)
      CALL EQVP
      IF (RN(1).EQ.999.9) GO TO 35
      NS=NS+1
      IF (NS.LE.LIMIT4) GO TO 20
      WRITE (IPR,52) LIMIT4
      GO TO 35
 20   DO 22 J=1,3
      IF (RD(J).EQ.0.) GO TO 21
      RD(J)=RN(J)/RD(J)
 21   TS(J,NS)=RD(J)
      FS(1,J,NS)=S1(J)
      FS(2,J,NS)=S2(J)
      FS(3,J,NS)=S3(J)
 22   CONTINUE
      GO TO 8
C-----C O N D I T  CARD
 23   READ (ILV,53) SYMWL,WL,TL,TH,NORM,IMAGE,SYMLP,IANO
C-----REPLACE BLANKS BY DEFAULT SYMBOLS
      IF (SYMWL.EQ.N3(19)) SYMWL=ISYMWL
      IF(TH.EQ.0.) TH=TH1
      IF(TH.GT.TH1) TH=TH1
      IF(TH.LT.TL)  TH=TL
      GO TO 8
C-----S P C G R P  CARD
 24   READ (ILV,54) (IGR(I),I=1,36)
      ISYST=0
      IGROUP=1
      CALL BURZ (ISYST,ISY,ISYB,NG)
      NS=NG
      NAG(NP)=NS
      SYMBR=ISYB
      ISYMCE=ISY
C-----MAKE ARRAY FROM BURZ COMPATIBLE WITH P U L V E R I X
      DO 25 I=1,3
      DO 25 IJ=1,3
      DO 25 IK=1,NS
      FS(I,IJ,IK)=SS(IK,IJ,I)
      TS(IJ,IK)=TSS(IK,IJ)
      ASS(NP,IK,IJ,I)=SS(IK,IJ,I)
      ATS(NP,IK,IJ)=TSS(IK,IJ)
 25   CONTINUE
C      DO 251 IK=1,NS
C      WRITE(IPR,2501)IK,((SS(IK,I,J),J=1,3),I=1,3),(TSS(IK,I),I=1,3)
C251   CONTINUE
C2501  FORMAT(9H0POSITION ,I3,10X,9F6.1,3F10.5)
      GO TO 8
C-----END OF FORMAT INTERPRETATION
 26   READ (ILV,43) INDF
C	CALL CLOSE(ILV)
C      OPEN(UNIT=IUN,NAME='XFACT.DON',TYPE='OLD',ACCESS='DIRECT',
C     *ASSOCIATEVARIABLE=IKF,RECORDSIZE=9,ERR=7347)
C      OPEN(UNIT=IDEUX,NAME='XANORM.DON',TYPE='OLD',ACCESS='DIRECT',
C     *ASSOCIATEVARIABLE=JKF,RECORDSIZE=2,ERR=7346)
261	IKF=1
	JKF=1
C-----CHECK FOR CELL AND ATOM CARD
      IF (NA(1).NE.0) GO TO 27
      WRITE (IPR,55)
      GO TO 36
 27   IF (A.NE.0.)GO TO 28
      WRITE (IPR,56)
      GO TO 36
C-----LORENTZ POLARISATION FACTOR
 28   KODLP=LP(SYMLP)
C-----CENTER OF SYMMETRY AT ORIGIN
      IF (CEN.EQ.LJC) ISYMCE=1
      IASYM(NP)=ISYMCE
C-----WAVELENGTH
      IF (WL.LT.0.02) WL=WAVE(SYMWL)
C-----LIMIT UPPER SIN**2 THETA VALUE FOR GUINIER CAMERA
      IF ((KODLP.GT.2).AND.(TH.GT.45.)) TH=THG
C-----TABULAR OUTPUT FEATURE
      IF (NORM.EQ.LBJ) INORM=0
      IF ((IANO.EQ.LBJ).AND.(ISYMCE.EQ.0).AND.(KODLP.NE.2)) INORM=2
      IF (NORM.EQ.LJA) INORM=1
C      IF (NORM.EQ.LJN) INORM=3
C-----DEFAULT SYMMETRY OPERATOR
      IF (NS.EQ.0) NS=1
C-----DERIVE BRAVAIS LATTICE INDICATOR
      IBRAVL=BRA(SYMBR)
      IABRA(NP)=IBRAVL
C-----CALCULATE MULTIPLICITIES OF SPECIAL ATOM POSITIONS
      CALL MULTF(TS,FS,X,Y,Z,FOCCU,FMULT,BTEMP)
C-----ANOMALOUS  DISPERSION INDICATOR
      DANO=0.
      IF ((IANO.EQ.LBJ).AND.(KODLP.NE.2)) ANO=1.
C-----CHECK CRYSTAL SYSTEM
      IF (ISYST.EQ.0) GO TO 29
      IF (ISYST.EQ.ISYSTM) GO TO 29
      WRITE (IPR,57)
C-----TAKE CRYSTAL SYSTEM FROM GROUP CARD
      ISYSTM=ISYST
C-----CALCULATE EXTINCTIONS,LAUE GROUP AND TRIGONAL SYMMETRY INDICATOR
 29   CALL EXTINC (ISYMCE,NS,TS,FS)
      IF (ISYSTM.EQ.6) ISYSTM=ITRIG
C-----RETRIEVE SCATTERING FACTORS FOR X RAY,NEUTRON AND ANOM.DISP.
      DO 33 I=1,NCOMPO
      FNEU=0.
      NC=I
      DELFR(I)=0.
      ASYMB=ELEMT(NC)
      DELFI(I)=0.
      IF (KODLP.NE.2) GO TO 31
C-----RETRIEVE NEUTRON SCATTERING LENGTH
      CALL ANOMA (SYMWL,ELEMT(NC),KODLP,IDEUX,JKF,FNEU)
      IF (FNEU.NE.0.) GO TO 30
      WRITE (IPR,58) ELEMT(NC)
      GO TO 36
 30   FNEUT(NC)=FNEU
      GO TO 33
 31   IF ( ANO .EQ.0.) GO TO 32
C-----RETRIEVE ANOMALOUS DISPERSION COEFFICIENTS
      CALL ANOMA (SYMWL,ASYMB,KODLP,IDEUX,JKF,FNEU)
      DELFR(NC)=DEL1
      DELFI(NC)=DEL2
C-----RETRIEVE CROMER-MANN COEFFICIENTS
32	CALL SYMBF(ASYMB,IKF)
	IF(IKF.NE.0)GO TO 321
	WRITE(IPR,322)ASYMB
322	FORMAT(1X,'Pas de table de facteur de forme pour : ',A4/)
	GO TO 36
321	CONTINUE !!READ(IUN'IKF)(FA(J,NC),FB(J,NC),J=1,4),FC(NC)		
 33   CONTINUE
C	CALL CLOSE(IUN)
C	CALL CLOSE(IDEUX)
C-----WRITE DATA FOR FOLLOWING PROGRAM PULVR2 ON UNIT ILU
      WRITE (ILU) (COMPND(I),I=1,19),A,B,C,ALPHA,BETA,GAMMA,WL,(IGR(I),I
     1=1,36),IGROUP, SYMWL, SYMLP
      WRITE (ILU) ISYSTM,ISYMCE,IBRAVL,NS,TL,TH,INORM,IMAGE,ANO,KODLP,NC
     1OMPO,(NA(I),I=1,8),IHOO,IOKO,IOOL,IHHL,IHOL,IHKO,IOKL,LAUE
      WRITE (ILU) ((TS(I,II),(FS(K,I,II),K=1,3),I=1,3),II=1,NS)
      DO 34 M=1,NCOMPO
      NL=NA(M)
      WRITE (ILU) DELFR(M),DELFI(M)
      WRITE (ILU) ELEMT(M),(FA(I,M),FB(I,M),I=1,4),FC(M),FNEUT(M)
      WRITE (ILU) (ELEMT(M),IDE(I,M),X(I,M),Y(I,M),Z(I,M),FMULT(I,M),FOC
     1CU(I,M),BTEMP(I,M),I=1,NL)
 34   CONTINUE
      WRITE (IPR,59) IJOB
      GO TO 37
C-----SKIP RECORDS UNTIL END CARD
 35   READ (ILV,43) INDF
      IF (INDF.NE.CAR(8)) GO TO 35
      READ(ILV,43) INDF
 36   WRITE (IPR,60) IJOB
C-----WRITE ONE DUMMY RECORD FOR BAD JOB
      A=-1.
      WRITE (ILU) (COMPND(I),I=1,19),A,B,C,ALPHA,BETA,GAMMA,WL,(IGR(I),I
     1=1,36),IGROUP
 37   CONTINUE
C-----END OF DATA PREPARATION
      REWIND ILU
      WRITE (IPR,61)
 38   FORMAT (/2X,'Date : ',9A1,5X,'Heure : ',8A1,
     *5X,'START *** LAZY ***'/)
 39   FORMAT (40A2)
391   FORMAT(40A2)
 40   FORMAT (//12H INPUT CARDS//4H JOB,I6//3H *.,7(10H*********.),1H*)
 41   FORMAT (3H * ,35A2,1H*)
 42   FORMAT (3H *.,7(10H*********.),1H*)
 43   FORMAT (A2)
 44   FORMAT (16H FORMAT LETTERS ,A2,15H NOT RECOGNIZED)
 45   FORMAT (6X,18A4,A2)
 46   FORMAT (7X,A4,A2,3(8A1),F6.2,F5.2)
 47   FORMAT (6H ONLY ,I5,19H ATOM KINDS ALLOWED)
 48   FORMAT (I5,9H ATOMS OF,A4,15H NUMBER ALLOWED,I5)
 49   FORMAT (13X,3F8.0,3F9.0)
 50   FORMAT (8X,A1,2X,A1)
 51   FORMAT (6X,45A1)
 52   FORMAT (10H MORE THAN,I5,13H SYMTRY CARDS)
 53   FORMAT (10X,A4,F6.0,2F5.0,1X,A1,I2,A4,1X,A1)
 54   FORMAT (6X,36A1)
 55   FORMAT (23H NO ATOM CARD WAS FOUND)
 56   FORMAT (23H NO CELL CARD WAS FOUND  )
 57   FORMAT (/12H * WARNING */,76H CRYSTAL SYSTEM SPECIFIED ON CELL CAR
     1D AND ON GROUP CARD ARE NOT CONSISTENT  )
 58   FORMAT (37H NEUTRON SCATTERING LENGTH FOR SYMBOL,2X,A4,19H HAS NOT
     1 BEEN FOUND)
 59   FORMAT (/2X,'Job ',I3,'   O K ',5X,'Fin d execution : ',8A1/)
 60   FORMAT (/5H JOB ,I5,7H FAILED//)
 61   FORMAT (/16H END OF  L A Z Y)
	RETURN
      END
      FUNCTION WAVE (SYML)
C-----DERIVES WAVELENGTH FOR RADIATION SYMBOL SYML
      COMMON/WAVEL/ CT
      DIMENSION CT(20), W(20)
      DATA W(1)/2.28970/,W(2)/2.29361/,W(3)/2.0848/,W(4)/2.2909/,W(5)/1.
     193604/,W(6)/1.93998/,W(7)/1.75653/,W(8)/1.9373/,W(9)/1.54056/,W(10
     2)/1.54439/,W(11)/1.39217/,W(12)/1.5418/,W(13)/0.70930/,W(14)/0.713
     359/,W(15)/0.63225/,W(16)/0.7107/,W(17)/0.55941/,W(18)/0.56380/,W(1
     49)/0.49701/,W(20)/0.5608/
      DO 1 I=1,20
      IF (SYML-CT(I)) 1,2,1
 1    CONTINUE
      WAVE=W(12)
      RETURN
 2    WAVE=W(I)
      RETURN
      END
      FUNCTION LP (SYMLP)
C-----ASSIGNS SEQUENCE NUMBER LP TO EACH LOR.POL. SYMBOL SYMLP
      COMMON /FLOR/ LPF,CS
      DIMENSION LPF(6), CS(6)
      DO 1 I=1,6
      IF (SYMLP-CS(I)) 1,2,1
 1    CONTINUE
      LP=LPF(1)
      RETURN
 2    LP=LPF(I)
      RETURN
      END
      FUNCTION BRA (SYMBR)
C-----ASSIGNS SEQUENCE NUMBER BRA TO BRAVAIS LATTICE SYMBOL SYMBR
      COMMON /BRAF/ IB,CU
      INTEGER CU,SYMBR
      DIMENSION IB(8), CU(8)
      DO 1 I=1,8
      IF (SYMBR-CU(I)) 1,2,1
 1    CONTINUE
      BRA=IB(1)
      RETURN
 2    BRA=IB(I)
      RETURN
      END
      SUBROUTINE SLASH(X,Y,Z)
C-----INTERPRETS COORDINATES GIVEN IN FRACTIONAL FORM
	character*1 IP,ID
      COMMON /SLAS/ IP(8,3)
      DIMENSION ID(13), FDE(2), IK(2), XYZ(3)
      DATA ID(1)/1H0/,ID(2)/1H1/,ID(3)/1H2/,ID(4)/1H3/,ID(5)/1H4/,ID(6)/
     11H5/,ID(7)/1H6/,ID(8)/1H7/,ID(9)/1H8/,ID(10)/1H9/,ID(11)/1H./,
     2ID(12)/1H-/,ID(13)/1H /
C-----NUMBER OF COLUMNS IN FORMAT FIELD OF ATOM CARD
      NFIELD=8
      DO 5 L=1,3
      IK(1)=1
      IK(2)=1
      FDE(1)=0
      FDE(2)=0
      NPOI=1
      X=1.
      IJ=1
      K=1
C-----LOOP OVER NUMBER OF FIELDS
      DO 3 I=1,NFIELD
      K=NFIELD+1-I
      DO 1 II=1,10
      IF (IP(K,L).EQ.ID(11)) NPOI=-1
      IF (IP(K,L).EQ.ID(12)) X=-1.
      IF (IP(K,L).EQ.ID(13)) GO TO 3
      IF (IP(K,L).EQ.ID(II)) GO TO 2
 1    CONTINUE
      IJ=2
      GO TO 3
 2    FDE(IJ)=FDE(IJ)+10**(IK(IJ)-1)*(II-1)
      IK(IJ)=IK(IJ)+1
 3    CONTINUE
      IF (FDE(1).NE.0.)GO TO 4
      XYZ(L)=0.
      GO TO 5
 4    IF (NPOI.NE.-1) X=X*FDE(2)/FDE(1)
      EX=-IK(1)+1
      IF (NPOI.EQ.-1) X=FDE(2)*X+X*FDE(1)*10.**EX
C-----MAKE COORDINATE POSITIVE
      IF (X.LT.-1.) X=X+1.
      XYZ(L)=X
 5    CONTINUE
      RETURN
      END
      SUBROUTINE EQVP
C-----DECODES EQUIVALENT POSITION CARD
      COMMON /UNITS/ ICR,IPR,ILU
      COMMON /POSIT/ RNN,RDD,S1N,SZN,S3N,IPOS
      DIMENSION IPOS(45), IC(18)
      DIMENSION RNN(3), RDD(3), S1N(3), SZN(3), S3N(3)
      DATA IC(1)/1HX/,IC(2)/1HY/,IC(3)/1HZ/,IC(4)/1H-/,IC(5)/1H,/,IC(6)/
     11H /,IC(7)/1H+/,IC(8)/1H//,IC(9)/1H0/,IC(10)/1H1/,IC(11)/1H2/,IC(1
     22)/1H3/,IC(13)/1H4/,IC(14)/1H5/,IC(15)/1H6/,IC(16)/1H7/,IC(17)/1H8
     3/,IC(18)/1H9/
      DO 1 J=1,3
      RDD(J)=0
      RNN(J)=0
      S1N(J)=0
      SZN(J)=0
      S3N(J)=0
 1    CONTINUE
      K=1
      J=1
      VZ=1.
C-----LOOP OVER ALL FIELDS
      DO 13 N=1,45
      DO 2 II=1,18
      IF (IPOS(N).NE.IC(II)) GO TO 2
      M=II
      IPOS(N)=IC(6)
      GO TO 3
 2    CONTINUE
      WRITE (IPR,15) IPOS(N)
      RNN(1)=999.9
      RETURN
 3    GO TO (7,8,9,10,11,13,13,13,4,4,4,4,4,4,4,4,4,4), M
 4    GO TO (5,6), K
 5    RNN(J)=M-9
      K=2
      GO TO 13
 6    RDD(J)=M-9
      K=1
      GO TO 13
 7    S1N(J)=VZ
      GO TO 12
 8    SZN(J)=VZ
      GO TO 12
 9    S3N(J)=VZ
      GO TO 12
 10   VZ=-1.
      GO TO 13
 11   J=J+1
      GO TO 13
 12   VZ=1.
 13   CONTINUE
      IF (J.EQ.3) GO TO 14
      WRITE (IPR,16)
      RNN(1)=999.9
 14   RETURN
C
 15   FORMAT (25H0WRONG CODE OF EQUIPOINT=,A1)
 16   FORMAT (22H0EQUIPOINT INCOMPLETE )
      END
      SUBROUTINE BURZ (ISYSTM,ISYMCE,IBRAVL,NG)
C-----ROUTINE TO INTERPRET HERMANN MAUGUIN SYMBOL FOR SPACE GROUP
C-----THIS ROUTINE HAS BEEN ADAPTED FROM A PROGRAM SUPPLIED BY
C-----PROF. BURZLAFF, UNIVERSITY OF ERLANGEN, GERMANY
      INTEGER E(3,3),ZEI(3,4),SYS,SS
      COMMON/BURC/TS,SS
      COMMON /POSIT/ RN,RD,S1,S2,S3,NT
      COMMON /UNITS/ NRD,NPT,ILU
      DIMENSION NT(45), IBRA(7), NMA(3), SH(3),TE(3)
      DIMENSION RN(3), RD(3), S1(3), S2(3), S3(3),ISYS(7)
      DIMENSION SS(24,3,3),TS(24,3)
      INTEGER N3(20)
      DATA ISYS/7,1,2,4,6,5,3/
      DATA IBRA/'P','A','B','C','F','I','R'/,NMA/3*0/,SH/3*0.25/
      DATA N3/'1','2','3','4',' ','6','A','B','C','D','M','N','P',
     1        ' ','/','-',4*' '/
C     WRITE (6,6020) NT
C6020 FORMAT(1X,76A1)
 1    NBL=-1
      NG=1
      NS=1
      DO 2 I=1,24
      DO 2 J=1,3
      TS(I,J)=0.0
      DO 2 K=1,3
      E(J,K)=0
      SS(I,J,K)=0
 2    CONTINUE
      SS(1,1,1)=1
      SS(1,2,2)=1
      SS(1,3,3)=1
      DO 3 I=1,3
      TE(I)=0.0
      DO 3 J=1,4
 3    ZEI(I,J)=0
      DO 8 I=1,36
      KXK=NT(I)
      IF (KXK.NE.N3(5)) GO TO 4
      NLQ=0
      IC=0
      GO TO 8
 4    IF (NBL.GE.0) GO TO 7
      DO 5 J=1,7
      NBR=J
C     WRITE(6,6004) KXK
C6004 FORMAT(1X,'BRAVAIS=',1X,A1)
      IF (KXK.EQ.IBRA(J)) GO TO 6
 5    CONTINUE
      NBR=8
 6    NBL=0
      IBRAVL=KXK
C     WRITE(6,6003) IBRAVL
C6003 FORMAT(1X,'BRAVAIS =',I3)
      GO TO 8
 7    IF (NLQ.EQ.0) NBL=NBL+1
      IC=IC+1
      ZEI(NBL,IC)=KXK
      NLQ=1
      IF (KXK.EQ.N3(15)) NS=0
 8    CONTINUE
      DO 9 I=1,4
      IF (ZEI(2,I).NE.N3(3)) GO TO 9
      SYS=6
      GO TO 15
 9    CONTINUE
      DO 11 I=1,4
      IF (ZEI(1,I).NE.N3(3).AND.ZEI(1,I).NE.N3(6)) GO TO 10
      SYS=5
      GO TO 15
 10   IF (ZEI(1,I).NE.N3(4)) GO TO 11
      SYS=4
      GO TO 15
 11   CONTINUE
      IF (NBL.GT.1) GO TO 14
      IF (ZEI(1,1).NE.N3(1).AND.ZEI(1,1).NE.N3(16)) GO TO 12
      SYS=1
      GO TO 15
 12   SYS=2
      DO 13 I=1,4
 13   ZEI(2,I)=ZEI(1,I)
      ZEI(1,1)=N3(1)
      ZEI(3,1)=N3(1)
 14   SYS=3
      IF (ZEI(1,1).EQ.N3(1).OR.ZEI(2,1).EQ.N3(1)) SYS=2
 15   GO TO (16,17,22,46,58,68), SYS
C-----TRICLINIC
 16   IF (ZEI(1,1).EQ.N3(16)) NS=0
      GO TO 76
C-----MONOCLINIC
 17   NG=2
      DO 18 I=1,3
 18   IF (ZEI(I,1).NE.N3(1)) IND=I
      ID=1
      IF (ZEI(IND,1).EQ.N3(2)) ID=-1
C     WRITE(6,6000) ID,IND
C6000 FORMAT(1X,'ID= ',I3,' IND= ',I3)
      DO 19 I=1,3
 19   SS(2,I,I)=SS(1,I,I)*ID
C     WRITE(6,6001) SS(2,3,3)
C6001 FORMAT(1X,'SS(2,3,3)=',F10.1)
      SS(2,IND,IND)=-SS(2,IND,IND)
C     WRITE(6,6001) SS(2,IND,IND)
      DO 21 I=1,3
      IF (ZEI(I,1).EQ.N3(2).AND.ZEI(I,2).EQ.N3(1)) TS(2,I)=0.5
      DO 21 J=1,4
      IF (ZEI(I,J).EQ.N3(7)) TS(2,1)=0.5
      IF (ZEI(I,J).EQ.N3(8)) TS(2,2)=0.5
      IF (ZEI(I,J).EQ.N3(9)) TS(2,3)=0.5
      IF (ZEI(I,J).EQ.N3(12)) GO TO 20
      GO TO 21
 20   K=I+1
      IF (K.GT.3) K=K-3
      TS(2,K)=0.5
      TS(2,6-K-I)=0.5
 21   CONTINUE
      GO TO 76
C-----ORTHORHOMBIC
 22   NG=4
      IC=0
      IND=1
      IF (ZEI(1,1).NE.N3(2).AND.ZEI(2,1).NE.N3(2).AND.ZEI(3,1).NE.N3(2))
     1IND=-1
      IF (IND.EQ.-1) NS=0
      DO 24 I=1,3
      ID=1
      IF (ZEI(I,1).EQ.N3(2)) ID=-1
      DO 23 J=1,3
 23   SS(1+I,J,J)=SS(1,J,J)*ID*IND
 24   SS(1+I,I,I)=-SS(1+I,I,I)
      DO 28 I=1,3
      IF (ZEI(I,1).EQ.N3(2).AND.ZEI(I,2).EQ.N3(1)) TS(1+I,I)=0.5
      DO 28 J=1,4
      IF (ZEI(I,J).EQ.N3(7)) TS(1+I,1)=0.5
      IF (ZEI(I,J).EQ.N3(8)) TS(1+I,2)=0.5
      IF (ZEI(I,J).EQ.N3(9)) TS(1+I,3)=0.5
      IF (ZEI(I,J).EQ.N3(12).OR.ZEI(I,J).EQ.N3(10)) GO TO 25
      GO TO 28
 25   K=I+1
      IF (K.GT.3) K=K-3
      IF (ZEI(I,J).EQ.N3(10)) GO TO 26
      TS(1+I,K)=0.5
      TS(1+I,6-K-I)=0.5
      GO TO 28
 26   IC=1
      IF (NS.EQ.1) GO TO 27
      TS(1+I,K)=0.25
      TS(1+I,6-K-I)=0.25
      GO TO 28
 27   TS(1+I,1)=0.25
      TS(1+I,2)=0.25
      TS(1+I,3)=0.25
 28   CONTINUE
      IF (IC.EQ.1) GO TO 76
      IF (NS.EQ.1) GO TO 36
      DO 29 I=1,3
      K=1+I
      IF (K.GT.3) K=K-3
      TC=TS(1+K,I)+TS(1+6-I-K,I)
      IF (TC.EQ.1.0) TC=0.0
 29   TS(1+I,I)=TC
C-----SPECIAL TREATMENT OF C M M A, C M C A, I M M A
      IF (NBR.EQ.1.OR.NBR.EQ.5) GO TO 76
      MA=0
      DO 31 I=1,3
      DO 30 J=1,4
 30   IF (ZEI(I,J).EQ.N3(11)) NMA(I)=1
 31   MA=MA+NMA(I)
      IF (NBR.EQ.6.AND.MA.EQ.2) GO TO 33
      IF (MA.EQ.0.OR.MA.EQ.3.OR.NBR.EQ.6) GO TO 76
      DO 32 I=1,3
      IF (NMA(NBR-1).EQ.1) GO TO 76
 32   SH(NBR-1)=0.
C-----ORIGIN SHIFT
 33   DO 35 I=1,NG
      DO 35 J=1,3
      DO 34 K=1,3
      ID=1
      IF (J.NE.K) ID=0
 34   TS(I,J)=TS(I,J)+(ID-SS(I,J,K))*SH(K)
      IF (TS(I,J).GT.1.) TS(I,J)=TS(I,J)-1.
 35   IF (TS(I,J).LT.1.0) TS(I,J)=TS(I,J)+1.
      GO TO 76
 36   IC=0
      DO 37 I=1,3
 37   IF (SS(1+I,1,1)*SS(1+I,2,2)*SS(1+I,3,3).EQ.-1) IC=1
      IF (IC.EQ.1) GO TO 41
      TC=TS(2,1)+TS(3,2)+TS(4,3)
      IF (TC.EQ.0.0) GO TO 76
      DO 40 I=1,3
      K=I+1
      IF (K.GT.3) K=K-3
      IF (TC.GT.0.5) GO TO 38
      IF (TS(1+I,I).EQ.0.0) GO TO 40
      M=I-1
      IF (M.EQ.0) M=M+3
      TS(1+M,I)=0.5
      GO TO 40
 38   IF (TC.GT.1.0) GO TO 39
      IF (TS(1+I,I).NE.0.0) GO TO 40
      L=K+1
      IF (L.GT.3) L=L-3
      TS(1+K,L)=0.5
      TS(1+L,K)=0.5
      GO TO 40
 39   TS(1+I,K)=0.5
 40   CONTINUE
      GO TO 76
 41   DO 42 I=1,3
 42   IF (SS(1+I,1,1)*SS(1+I,2,2)*SS(1+I,3,3).EQ.1) ID=I
      DO 45 I=1,3
      TC=TS(2,I)+TS(3,I)+TS(4,I)
      IF (TC.EQ.0.0.OR.TC.EQ.1.0) GO TO 45
      IF (ZEI(1,1).EQ.N3(11).AND.ZEI(2,1).EQ.N3(12).OR.ZEI(2,1).EQ.
     1N3(11).AND.ZEI(3,1).EQ.N3(12).OR.ZEI(3,1).EQ.N3(11).AND.ZEI(1,1)
     2.EQ.N3(12)) GO TO 44
      DO 43 J=1,3
      IF (ID.EQ.J) GO TO 43
      IF (TS(1+J,I).EQ.0.5) GO TO 43
      TS(1+J,I)=0.5
 43   CONTINUE
      GO TO 45
 44   K=I-1
      IF (K.EQ.0) K=K+3
      TS(1+K,I)=0.5
 45   CONTINUE
      GO TO 76
C-----TETRAGONAL
 46   NG=4
      IF (NBL.EQ.3) NG=8
      SS(2,1,2)=-1
      SS(2,2,1)=1
      SS(2,3,3)=1
      M=ZEI(1,1)
      N=ZEI(1,2)
      DO 47 I=1,3
      DO 47 J=1,3
 47   IF (M.EQ.N3(16)) SS(2,I,J)=-SS(2,I,J)
      IF (M.EQ.N3(16)) GO TO 50
      IF (N.EQ.N3(1)) TS(2,3)=0.25
      IF (N.EQ.N3(2)) TS(2,3)=0.5
      IF (N.EQ.N3(3)) TS(2,3)=0.75
      IF (ZEI(1,3).EQ.N3(12).OR.(ZEI(1,4).EQ.N3(12).AND.NBL.EQ.3))
     1TS(2,1)=0.5
      IF ((ZEI(1,4).EQ.N3(12).AND.NBL.EQ.1).OR.(N.EQ.N3(1).AND.NS.EQ.1.
     1AND.NBR.EQ.6)) TS(2,2)=0.5
      IF (N.EQ.N3(1).AND.NS.EQ.0.AND.NBR.EQ.6) GO TO 48
      IF (ZEI(2,2).EQ.N3(1).OR.(ZEI(1,4).NE.N3(12).AND.ZEI(2,1).EQ.
     1N3(12).AND.ZEI(3,1).EQ.N3(11))) GO TO 49
      GO TO 50
 48   TS(2,1)=0.25
      TS(2,2)=0.75
      IF (NBL.EQ.1) TS(2,1)=0.75
      IF (NBL.EQ.1) TS(2,2)=0.25
      GO TO 50
 49   TS(2,1)=0.5
      TS(2,2)=0.5
 50   SS(3,1,1)=-1
      SS(3,2,2)=-1
      SS(3,3,3)=1
      TS(3,1)=SS(2,1,2)*TS(2,2)+TS(2,1)
      TS(3,2)=SS(2,2,1)*TS(2,1)+TS(2,2)
      TS(3,3)=SS(2,3,3)*TS(2,3)+TS(2,3)
      DO 51 I=1,3
 51   IF (NBR.EQ.6.AND.TS(3,1).EQ.0.5.AND.TS(3,2).EQ.0.5.AND.TS(3,3).EQ.
     10.5) TS(3,I)=0.0
      DO 52 I=1,3
      TS(4,I)=TS(2,I)
      DO 52 J=1,3
      TS(4,I)=TS(4,I)+SS(2,I,J)*TS(3,J)
      DO 52 K=1,3
 52   SS(4,I,J)=SS(4,I,J)+SS(2,I,K)*SS(3,K,J)
      IF (NBL.EQ.1) GO TO 76
      IF (NS.EQ.0) GO TO 56
      M=ZEI(2,1)
      N=ZEI(3,1)
      IF (M.NE.N3(2).AND.N.NE.N3(2)) GO TO 55
      IF (M.EQ.N3(2).AND.N.EQ.N3(2)) GO TO 54
      IF (M.EQ.N3(2)) GO TO 53
      IF (M.EQ.N3(9).OR.M.EQ.N3(12)) TE(3)=0.5
      E(1,1)=-1
      E(2,2)=1
      E(3,3)=1
      IF (M.NE.N3(12).AND.M.NE.N3(8)) GO TO 57
      TE(1)=0.5
      TE(2)=0.5
      GO TO 57
 53   E(1,1)=1
      E(2,2)=-1
      E(3,3)=-1
      IF (N.EQ.N3(9)) TE(3)=0.5
      IF (N.EQ.N3(10)) TE(3)=0.25
      IF (N.EQ.N3(10)) TE(2)=0.5
      IF (ZEI(2,2).NE.N3(1)) GO TO 57
      TE(1)=0.5
      TE(2)=0.5
      GO TO 57
 54   E(1,2)=1
      E(2,1)=1
      E(3,3)=-1
      IF (ZEI(2,2).NE.0.OR.NBR.EQ.6.OR.ZEI(1,2).EQ.0) GO TO 57
      IF (ZEI(1,2).EQ.N3(1)) TE(3)=0.75
      IF (ZEI(1,2).EQ.N3(2)) TE(3)=0.5
      IF (ZEI(1,2).EQ.N3(3)) TE(3)=0.25
      GO TO 57
 55   M=ZEI(2,1)
      E(1,1)=-1
      E(2,2)=1
      E(3,3)=1
      IF (M.EQ.N3(9).OR.M.EQ.N3(12)) TE(3)=0.5
      IF (M.EQ.N3(12).OR.M.EQ.N3(8)) TE(1)=0.5
      IF (M.EQ.N3(12).OR.M.EQ.N3(8)) TE(2)=0.5
      GO TO 57
 56   E(1,1)=-1
      E(2,2)=1
      E(3,3)=1
      IF (ZEI(2,1).EQ.N3(9).OR.ZEI(2,1).EQ.N3(12)) TE(3)=0.5
      IF (ZEI(2,1).EQ.N3(8).OR.ZEI(2,1).EQ.N3(12)) TE(2)=0.5
      IF (ZEI(2,1).EQ.N3(8).OR.ZEI(2,1).EQ.N3(12)) TE(1)=0.5
      IF (ZEI(1,3).EQ.N3(12).OR.ZEI(1,4).EQ.N3(12)) TE(1)=TE(1)+0.5
 57   NE=4
      GO TO 74
C-----HEXAGONAL
 58   NG=3
      M=ZEI(1,1)
      N=ZEI(1,2)
      IF (M.EQ.N3(16).AND.N.EQ.N3(3)) NS=0
      IF (M.EQ.N3(6)) GO TO 61
      SS(2,1,2)=-1
      SS(2,2,1)=1
      SS(2,2,2)=-1
      SS(2,3,3)=1
      IF (N.EQ.N3(1)) TS(2,3)=1.0/3.0
      IF (N.EQ.N3(2)) TS(2,3)=2.0/3.0
      SS(3,1,1)=-1
      SS(3,2,1)=-1
      SS(3,1,2)=1
      SS(3,3,3)=1
      TS(3,3)=2.0*TS(2,3)
      IF (TS(3,3).GE.1.0) TS(3,3)=TS(3,3)-1.0
      IF (NBL.EQ.1.AND.N.NE.N3(6)) GO TO 76
      IF (N.NE.N3(6)) GO TO 60
      NG=NG+NG
      DO 59 I=1,3
      DO 59 J=1,3
      DO 59 K=1,3
      SS(3+I,J,K)=SS(I,J,K)
 59   SS(3+I,3,3)=-1
 60   IF (NBL.EQ.1) GO TO 76
      IF (ZEI(2,1).NE.N3(9).AND.ZEI(3,1).NE.N3(9)) GO TO 63
      TS(4,3)=0.5
      TS(5,3)=0.5
      TS(6,3)=0.5
      GO TO 63
 61   NG=NG+NG
      SS(2,1,1)=1
      SS(2,1,2)=-1
      SS(2,2,1)=1
      SS(2,3,3)=1
      IF (N.EQ.N3(1)) TS(2,3)=1.0/6.0
      IF (N.EQ.N3(2)) TS(2,3)=2.0/6.0
      IF (N.EQ.N3(3)) TS(2,3)=3.0/6.0
      IF (N.EQ.N3(4)) TS(2,3)=4.0/6.0
      IF (N.EQ.N3(5)) TS(2,3)=5.0/6.0
      DO 62 I=1,4
      DO 62 J=1,3
      TS(2+I,J)=TS(2,J)
      DO 62 K=1,3
      TS(2+I,J)=TS(2+I,J)+SS(2,J,K)*TS(1+I,K)
      IF (TS(2+I,J).GT.1.0) TS(2+I,J)=TS(2+I,J)-1.0
      DO 62 L=1,3
 62   SS(2+I,J,K)=SS(2+I,J,K)+SS(2,J,L)*SS(1+I,L,K)
      IF (NBL.EQ.1) GO TO 76
 63   NG=NG+NG
      M=ZEI(2,1)
      N=ZEI(3,1)
      IF (M.EQ.N3(1)) GO TO 65
      IF (M.EQ.N3(2)) GO TO 64
      E(1,2)=-1
      E(2,1)=-1
      E(3,3)=1
      IF (M.EQ.N3(9)) TE(3)=0.5
      GO TO 67
 64   E(1,2)=1
      E(2,1)=1
      E(3,3)=-1
      TE(3)=2.0*TS(2,3)
C-----GROUP P 31 I 2 AND P 32 I 2
      IF (ZEI(1,1).EQ.N3(3).AND.(ZEI(1,2).EQ.N3(1).OR.ZEI(1,2).EQ.
     1N3(2))) TE(3)=0.
      GO TO 67
 65   IF (N.EQ.N3(2)) GO TO 66
      E(1,2)=1
      E(2,1)=1
      E(3,3)=1
      IF (N.EQ.N3(9)) TE(3)=0.5
      GO TO 67
 66   E(1,2)=-1
      E(2,1)=-1
      E(3,3)=-1
      TE(3)=2.0*TS(2,3)
      IF (TE(3).GT.1.0) TE(3)=TE(3)-1.0
 67   NE=6
      IF (ZEI(1,1).EQ.N3(3).OR.(ZEI(1,2).EQ.N3(3).AND.ZEI(1,1).EQ.
     1N3(16))) NE=3
      GO TO 74
C-----CUBIC
 68   NG=12
      IF (NBL.EQ.3) NG=24
      IF (ZEI(1,1).NE.N3(2).AND.ZEI(1,1).NE.N3(4).AND.ZEI(1,1).NE.
     1N3(16)) NS=0
      DO 69 I=1,3
      DO 69 J=1,3
      SS(1+I,J,J)=1
      IF (I.EQ.J) GO TO 69
      SS(1+I,J,J)=-1
      IF (ZEI(1,1).EQ.N3(12)) TS(1+I,J)=0.5
      IF (ZEI(1,1).EQ.N3(10)) TS(1+I,J)=0.25
 69   CONTINUE
      IF (ZEI(1,1).NE.N3(7).AND.ZEI(3,1).NE.N3(10).AND.ZEI(1,2).NE.N3(3)
     1.AND.ZEI(1,2).NE.N3(1).OR.NBR.EQ.5) GO TO 71
      DO 70 I=1,3
      TS(1+I,I)=0.5
      K=I+1
      IF (K.EQ.4) K=1
 70   TS(1+I,K)=0.5
 71   DO 72 I=1,4
      DO 72 J=1,3
      DO 72 K=1,3
      L=J+1
      IF (L.EQ.4) L=1
      M=J-1
      IF (M.EQ.0) M=3
      SS(4+I,J,K)=SS(I,L,K)
      SS(8+I,J,K)=SS(I,M,K)
      TS(4+I,J)=TS(I,L)
 72   TS(8+I,J)=TS(I,M)
      IF (NG.EQ.12) GO TO 76
      NE=12
      E(1,2)=1
      E(2,1)=1
      E(3,3)=1
      IF (ZEI(3,1).EQ.N3(2)) E(3,3)=-1
      IF (ZEI(3,1).EQ.N3(9)) TE(3)=0.5
      DO 73 I=1,3
      IF (ZEI(3,1).EQ.N3(12).OR.ZEI(1,2).EQ.N3(2)) TE(I)=0.5
 73   IF (ZEI(3,1).EQ.N3(10).OR.ZEI(1,2).EQ.N3(1).OR.ZEI(1,2).EQ.N3(3))
     1TE(I)=0.25
      IF (ZEI(1,2).EQ.N3(1).AND.NBR.EQ.1) TE(1)=0.75
      IF ((ZEI(1,2).NE.N3(1).OR.NBR.NE.6).AND.(ZEI(1,2).NE.N3(3).OR.NBR
     1.NE.1)) GO TO 74
      TE(2)=0.75
      TE(3)=0.75
 74   DO 75 I=1,NE
      DO 75 J=1,3
      TS(NE+I,J)=TE(J)
      DO 75 K=1,3
      TS(NE+I,J)=TS(NE+I,J)+E(J,K)*TS(I,K)
      DO 75 L=1,3
 75   SS(NE+I,J,K)=SS(NE+I,J,K)+E(J,L)*SS(I,L,K)
 76   DO 81 I=1,NG
      DO 81 J=1,3
 77   IF (TS(I,J).GE.1.0) GO TO 78
      GO TO 79
 78   TS(I,J)=TS(I,J)-1.0
      GO TO 77
 79   IF (TS(I,J).LT.0.0) GO TO 80
      GO TO 81
 80   TS(I,J)=TS(I,J)+1.0
      GO TO 79
 81   CONTINUE
      ISYSTM=ISYS(SYS)
      ISYMCE=1-NS
C     WRITE(6,6010) ISYMCE,NG
C6010 FORMAT(' ISYMCE=',I3,' NG=',I3)
      RETURN
      END
      SUBROUTINE EXTINC (ISYMCE,NS,TS,FS)
C-----FINDS EXTINCTIONS, LAUE GROUP AND HEXAGONAL SYMMETRY INDICATOR
      COMMON /EXTI/ IHOO,IOKO,IOOL,IHKO,IHOL,IOKL,IHHL,ILAU,ITRIG
      COMMON /UNITS/ NRD,NPT,ILU
      DIMENSION TS(3,24), FS(3,3,24)
      ILAU=1
      Q1=1./3.
      Q2=1./6.
      Q3=2./3.
      Q4=5./6.
      DO 2 I=1,NS
      POIN=0.
      R=TS(1,I)
      S=TS(2,I)
      T=TS(3,I)
      X=FS(1,1,I)*10.+FS(2,1,I)*50.+FS(3,1,I)*100.
      Y=FS(1,2,I)*10.+FS(2,2,I)*50.+FS(3,2,I)*100.
      Z=FS(1,3,I)*10.+FS(2,3,I)*50.+FS(3,3,I)*100.
      XO=ABS(X)
      YO=ABS(Y)
      ZO=ABS(Z)
      IF ((R.EQ..5).AND.(XO.EQ.10.)) IHOO=2
      IF ((S.EQ..5).AND.(YO.EQ.50.)) IOKO=2
      IF (IOOL.GT.3) GO TO 1
      IF ((T.EQ..5).AND.(ZO.EQ.100.)) IOOL=2
      IF ((T.EQ.Q2).OR.(T.EQ.Q4)) IOOL=6
      IF ((T.EQ.Q1).OR.(T.EQ.Q3)) IOOL=3
      IF ((T.EQ..25).OR.(T.EQ..75)) IOOL=4
 1    IF ((X.EQ.50.).AND.(Y.EQ.10.)) ILAU=2
      IF ((X.EQ.-50.00).AND.(Y.EQ.-10.00)) ILAU=2
      IF ((X.EQ.-40.).AND.(Y.EQ.10.).AND.(Z.EQ.100.)) ITRIG=6
      IF ((X.EQ.40.00).AND.(Y.EQ.-10.00).AND.(Z.EQ.-100.00)) ITRIG=6
      IF (((S.EQ..25).OR.(S.EQ..75)).AND.(YO.EQ.50.)) IOKO=4
      IF (((R.EQ..25).OR.(R.EQ..75)).AND.(XO.EQ.10.)) IHOO=4
      X=X+R
      Y=Y+S
      Z=Z+T
      IF ((X.EQ.10.5).AND.(Y.EQ.50.5)) IHKO=2
      IF ((X.EQ.10.0).AND.(Y.EQ.50.5)) IHKO=3
      IF ((X.EQ.10.25).AND.(Y.EQ.50.25)) IHKO=4
      IF ((X.EQ.10.75).AND.(Y.EQ.50.75)) IHKO=4
      IF ((X.EQ.10.50).AND.(Y.EQ.50.00)) IHKO=5
      IF ((Y.EQ.50.50).AND.(Z.EQ.100.50)) IOKL=2
      IF ((Y.EQ.50.00).AND.(Z.EQ.100.50)) IOKL=3
      IF ((Y.EQ.50.25).AND.(Z.EQ.100.25)) IOKL=4
      IF ((Y.EQ.50.75).AND.(Z.EQ.100.75)) IOKL=4
      IF ((Y.EQ.50.50).AND.(Z.EQ.100.00)) IOKL=5
      IF ((X.EQ.10.5).AND.(Z.EQ.100.50)) IHOL=2
      IF ((X.EQ.10.0).AND.(Z.EQ.100.50)) IHOL=3
      IF ((X.EQ.10.25).AND.(Z.EQ.100.25)) IHOL=4
      IF ((X.EQ.10.75).AND.(Z.EQ.100.75)) IHOL=4
      IF ((X.EQ.10.5).AND.(Z.EQ.100.0)) IHOL=5
      IF ((X.EQ.50.50).AND.(Y.EQ.10.5).AND.(Z.EQ.100.50)) IHHL=2
      IF ((X.EQ.50.00).AND.(Y.EQ.10.0).AND.(Z.EQ.100.50)) IHHL=2
      IF ((X.EQ.50.00).AND.(Y.EQ.10.00).AND.(Z.EQ.100.50)) IHHL=2
      IF ((X.EQ.50.00).AND.(Y.EQ.10.5).AND.(Z.EQ.100.25)) IHHL=3
      IF ((X.EQ.50.00).AND.(Y.EQ.10.5).AND.(Z.EQ.100.75)) IHHL=3
      IF ((X.EQ.50.75).AND.(Y.EQ.10.75).AND.(Z.EQ.100.75)) IHHL=3
      IF ((X.EQ.50.75).AND.(Y.EQ.10.75).AND.(Z.EQ.100.25)) IHHL=3
      IF ((X.EQ.50.25).AND.(Y.EQ.10.25).AND.(Z.EQ.100.25)) IHHL=3
C-----CHECK CENTROSYMMETRIC POSITION
      IF (ISYMCE.EQ.0) GO TO 2
      IF (POIN.EQ.-1.) GO TO 2
      POIN=-1.
      X=-X+R
      Y=-Y+S
      Z=-Z+T
      IF (R.NE.0.) R=1.-R
      IF (S.NE.0.) S=1.-S
      IF (T.NE.0.) T=1.-T
      GO TO 1
 2    CONTINUE
      RETURN
      END
      SUBROUTINE MULTF(TS,FS,X,Y,Z,FOCCU,FMULT,BTEMP)
C-----CALCULATES MULTIPLICITIES OF SPECIAL POSITIONS
	character*1 NORM,IANO
	REAL IELMT
      INTEGER SYMBR
      DIMENSION X(50,8),Y(50,8),Z(50,8),FOCCU(50,8),FMULT(50,8),
     *BTEMP(50,8),TS(3,24),FS(3,3,24)
      DIMENSION COMPND(19),IELMT(8),FNEUT(8),NA(8),DELFR(8),DELFI(8)
     *,B1(3,9),TSB(3),XYZ(3),XYZ1(3)
      COMMON /INPUT/ COMPND,IELMT,FNEUT,A,B,C,ALPHA,BE
     1TA,GAMMA,SYMSY,SYMBR,ISYMCE,NCOMPO,NA,SYMWL,WL,SL,SH,IMAGE,SYMLP,
     2AGUIN,BGUIN,DELFR,DELFI,NS,IBRAVL,NORM,IANO
      COMMON /UNITS/ ICR,IPR,ILU
      DATA B1(1,1)/0./,B1(2,1)/0./,B1(3,1)/0./,B1(1,2)/0.5/,B1(2,2)/0.5/
     1,B1(3,2)/0.5/,B1(1,3)/0.66667/,B1(2,3)/0.33333/,B1(3,3)/0.33333/,B
     21(1,4)/0.5/,B1(2,4)/0.5/,B1(3,4)/0./,B1(1,5)/0./,B1(2,5)/0.5/,B1(3
     3,5)/0.5/,B1(1,6)/0.5/,B1(2,6)/0./,B1(3,6)/0.5/,B1(1,7)/0.5/,B1(2,7
     4)/0.5/,B1(3,7)/0.0/,B1(1,8)/0.33333/,B1(2,8)/0.66667/,B1(3,8)/0.66
     5667/
      NBRA=1
      IF (IBRAVL.GT.1) NBRA=2
      IF (IBRAVL.EQ.3) NBRA=3
      IF (IBRAVL.EQ.4) NBRA=4
C-----LOOP OVER ATOMKINDS
      DO 7 IC=1,NCOMPO
      NATOM=NA(IC)
C-----LOOP OVER ATOMS OF ONE KIND
      DO 6 IA=1,NATOM
      XYZ1(1)=X(IA,IC)
      XYZ1(2)=Y(IA,IC)
      XYZ1(3)=Z(IA,IC)
C-----MAKE COORDINATES POSITIVE
      DO 1 I=1,3
 1    IF (XYZ1(I).LT.0.) XYZ1(I)=XYZ1(I)+1.
      FMULT(IA,IC)=0.
C-----LOOP OVER EQUIVALENT POSITIONS
      DO 4 J=1,NS
C-----LOOP OVER BRAVAIS LATTICE POINTS
      DO 4 NB=1,NBRA
      ANTI=1.
 2    DIF=0.
C-----CALCULATE ATOM COORDINATES
      DO 3 I=1,3
      XYZ(I)=ANTI*(TS(I,J)+FS(1,I,J)*XYZ1(1)+FS(2,I,J)*XYZ1(2)+FS(3,I,J)
     1*XYZ1(3)) +0.00001
      IF (NB.EQ.1) TSB(I)=B1(I,1)
      IF (NB.EQ.2) TSB(I)=B1(I,IBRAVL)
      IF (NB.EQ.4) TSB(I)=B1(I,6)
      IF ((NB.EQ.3).AND.(IBRAVL.EQ.3)) TSB(I)=B1(I,8)
      IF ((NB.EQ.3).AND.(IBRAVL.EQ.4)) TSB(I)=B1(I,5)
C-----ADD BRAVAIS LATTICE VECTORS
      XYZ(I)=XYZ(I)+TSB(I)
C-----MAKE COORDINATES POSITIVE AND LESS THAN 1.
      IF (XYZ(I).GE.1.) XYZ(I)=XYZ(I)-1.
      IF (XYZ(I).LT.-1.) XYZ(I)=XYZ(I)+1.
      IF (XYZ(I).LT.0.) XYZ(I)=XYZ(I)+1.
C-----CALCULATE NUMBER FMULT OF COINCIDING ATOMS
 3    CONTINUE
      DIF=XYZ(1)-XYZ1(1)
      DIF=ABS(DIF)
      DIF1=XYZ(2)-XYZ1(2)
      DIF1=ABS(DIF1)
      DIF=DIF+DIF1
      DIF1=XYZ(3)-XYZ1(3)
      DIF1=ABS(DIF1)
      DIF=DIF+DIF1
      IF (DIF.LT..001) FMULT(IA,IC)=FMULT(IA,IC)+1.
C-----CHECK CENTROSYMMETRICALLY RELATED ATOMS
      IF (ISYMCE.NE.1) GO TO 4
      IF (ANTI.EQ.-1.) GO TO 4
      ANTI=-1.
      GO TO 2
 4    CONTINUE
      IF (FMULT(IA,IC).NE.0.) GO TO 5
      A=-1.
      WRITE (IPR,8) IA,IC
 5    FMULT(IA,IC)=1./FMULT(IA,IC)
 6    CONTINUE
 7    CONTINUE
      RETURN
C
 8    FORMAT (22H WRONG MULTIPLICITY OF,I5,16H TH ATOM OF TYPE,I5,43H CH
     1ECK COORDINATES AND EQUIVALENT POSITIONS)
      END
      SUBROUTINE SYMBF (ASYMB,IELMT)
C-----FINDS THE SEQUENCE NUMBER IELMT OF ELEMENT ASYMB AMONG ELEMENTS
C-----FOR WHICH SCATTERING CURVES EXIST IN ROUTINE CONFS
      DIMENSION S(214)
      DATA S(1)/4HH   /,S(2)/4HH.  /,S(3)/4HH1- /,S(4)/4HHE  /,S(5)/4HLI
     1  /,S(6)/4HLI1+/,S(7)/4HBE  /,S(8)/4HBE2+/,S(9)/4HB   /,S(10)/4HC 
     2  /,S(11)/4HC.  /,S(12)/4HN   /,S(13)/4HO   /,S(14)/4HO1- /,S(15)/
     34HF   /,S(16)/4HF1- /,S(17)/4HNE  /,S(18)/4HNA  /,S(19)/4HNA1+/,S(
     420)/4HMG  /,S(21)/4HMG2+/,S(22)/4HAL  /,S(23)/4HAL3+/,S(24)/4HSI  
     5/,S(25)/4HSI. /,S(26)/4HSI4+/,S(27)/4HS   /,S(28)/4HP   /,S(29)/4H
     6CL  /,S(30)/4HCL1-/,S(31)/4HAR  /,S(32)/4HK   /,S(33)/4HK1+ /,S(34
     7)/4HCA  /,S(35)/4HCA2+/,S(36)/4HSC  /,S(37)/4HSC3+/,S(38)/4HTI  /,
     8S(39)/4HTI2+/,S(40)/4HTI3+/
      DATA S(41)/4HTI4+/,S(42)/4HV   /,S(43)/4HV2+ /,S(44)/4HV3+ /,S(45)
     1/4HV5+ /,S(46)/4HCR  /,S(47)/4HCR2+/,S(48)/4HCR3+/,S(49)/4HMN  /,S
     2(50)/4HMN2+/,S(51)/4HMN3+/,S(52)/4HMN4+/,S(53)/4HFE  /,S(54)/4HFE+
     32/,S(55)/4HFE3+/,S(56)/4HCO  /,S(57)/4HCO2+/,S(58)/4HCO3+/,S(59)/4
     4HNI  /,S(60)/4HNI2+/,S(61)/4HNI3+/,S(62)/4HCU  /,S(63)/4HCU1+/,S(6
     54)/4HCU2+/,S(65)/4HZN  /,S(66)/4HZN2+/,S(67)/4HGA  /,S(68)/4HGA3+/
     6,S(69)/4HGE  /,S(70)/4HGE4+/,S(71)/4HAS  /,S(72)/4HSE  /,S(73)/4HB
     7R  /,S(74)/4HBR1-/,S(75)/4HKR  /,S(76)/4HRB  /,S(77)/4HRB1+/,S(78)
     8/4HSR  /,S(79)/4HSR2+/,S(80)/4HY   /
      DATA S(81)/4HY3+ /,S(82)/4HZR  /,S(83)/4HZR4+/,S(84)/4HNB  /,S(85)
     1/4HNB3+/,S(86)/4HNB5+/,S(87)/4HMO  /,S(88)/4HMO3+/,S(89)/4HMO5+/,S
     2(90)/4HMO6+/,S(91)/4HTC  /,S(92)/4HRU  /,S(93)/4HRU3+/,S(94)/4HRU+
     34/,S(95)/4HRH  /,S(96)/4HRH3+/,S(97)/4HRH4+/,S(98)/4HPD  /,S(99)/4
     4HPD2+/,S(100)/4HPD4+/,S(101)/4HAG  /,S(102)/4HAG1+/,S(103)/4HAG2+/
     5,S(104)/4HCD  /,S(105)/4HCD2+/,S(106)/4HIN  /,S(107)/4HIN3+/,S(108
     6)/4HSN  /,S(109)/4HSN2+/,S(110)/4HSN4+/,S(111)/4HSB  /,S(112)/4HSB
     73+/,S(113)/4HSB5+/,S(114)/4HTE  /,S(115)/4HI   /,S(116)/4HI1- /,S(
     8117)/4HXE  /,S(118)/4HCS  /,S(119)/4HCS1+/,S(120)/4HBA  /
      DATA S(121)/4HBA2+/,S(122)/4HLA  /,S(123)/4HLA3+/,S(124)/4HCE  /,S
     1(125)/4HCE3+/,S(126)/4HCE4+/,S(127)/4HPR  /,S(128)/4HPR3+/,S(129)/
     24HPR4+/,S(130)/4HND  /,S(131)/4HND3+/,S(132)/4HPM  /,S(133)/4HPM3+
     3/,S(134)/4HSM  /,S(135)/4HSM3+/,S(136)/4HEU  /,S(137)/4HEU2+/,S(13
     48)/4HEU3+/,S(139)/4HGD  /,S(140)/4HGD3+/,S(141)/4HTB  /,S(142)/4HT
     5B3+/,S(143)/4HDY  /,S(144)/4HDY3+/,S(145)/4HHO  /,S(146)/4HHO3+/,S
     6(147)/4HER  /,S(148)/4HER3+/,S(149)/4HTM  /,S(150)/4HTM3+/,S(151)/
     74HYB  /,S(152)/4HYB2+/,S(153)/4HYB3+/,S(154)/4HLU  /,S(155)/4HLU3+
     8/,S(156)/4HHF  /,S(157)/4HHF4+/,S(158)/4HTA  /,S(159)/4HTA5+/,S(16
     90)/4HW   /
      DATA S(161)/4HW6+ /,S(162)/4HRE  /,S(163)/4HOS  /,S(164)/4HOS4+/,S
     1(165)/4HIR  /,S(166)/4HIR3+/,S(167)/4HIR4+/,S(168)/4HPT  /,S(169)/
     24HPT2+/,S(170)/4HPT4+/,S(171)/4HAU  /,S(172)/4HAU1+/,S(173)/4HAU3+
     3/,S(174)/4HHG  /,S(175)/4HHG1+/,S(176)/4HHG2+/,S(177)/4HTL  /,S(17
     48)/4HTL1+/,S(179)/4HTL3+/,S(180)/4HPB  /,S(181)/4HPB2+/,S(182)/4HP
     5B4+/,S(183)/4HBI  /,S(184)/4HBI3+/,S(185)/4HBI5+/,S(186)/4HPO  /,S
     6(187)/4HAT  /,S(188)/4HRN  /,S(189)/4HFR  /,S(190)/4HRA  /,S(191)/
     74HRA2+/,S(192)/4HAC  /,S(193)/4HAC3+/,S(194)/4HTH  /,S(195)/4HTH4+
     8/,S(196)/4HPA  /,S(197)/4HU   /,S(198)/4HU3+ /,S(199)/4HU4+ /,S(20
     90)/4HU6+ /
      DATA S(201)/4HNP  /,S(202)/4HNP3+/,S(203)/4HNP4+/,S(204)/4HNP6+/,S
     1(205)/4HPU  /,S(206)/4HPU3+/,S(207)/4HPU4+/,S(208)/4HPU6+/,S(209)/
     24HAM  /,S(210)/4HCM  /,S(211)/4HBK  /,S(212)/4HCF  /,
     3S(213)/4HO2-./,S(214)/4H    /
      DO 1 I=1,214
      IF (ASYMB-S(I)) 1,2,1
 1    CONTINUE
      I=0
 2    IELMT=I
      RETURN
      END
      SUBROUTINE ANOMA (ANODE,ELEMEN,KODLP,ID,IN,FNEU)
C-----CALCULATE ANOM DISPERSION COEFFICIENTS AND NEUTRON SCATT.LENGTH
      REAL M,N
      COMMON /ANOMAL/ DELFR,DELFI
      COMMON /UNITS/ ICR,IPR,ILU
      COMMON /WAVEL/ M
      DIMENSION N(98), M(20)
      DATA N(1)/4HLI  /,N(2)/4HBE  /,N(3)/4HB   /,N(4)/4HC   /,N(5)/4HN 
     1  /,N(6)/4HO   /,N(7)/4HF   /,N(8)/4HNE  /,N(9)/4HNA  /,N(10)/4HMG
     2  /,N(11)/4HAL  /,N(12)/4HSI  /,N(13)/4HP   /,N(14)/4HS   /,N(15)/
     34HCL  /,N(16)/4HAR  /,N(17)/4HK   /,N(18)/4HCA  /,N(19)/4HSC  /,N(
     420)/4HTI  /,N(21)/4HV   /,N(22)/4HCR  /,N(23)/4HMN  /,N(24)/4HFE  
     5/,N(25)/4HCO  /,N(26)/4HNI  /,N(27)/4HCU  /,N(28)/4HZN  /,N(29)/4H
     6GA  /,N(30)/4HGE  /,N(31)/4HAS  /,N(32)/4HSE  /,N(33)/4HBR  /,N(34
     7)/4HKR  /,N(35)/4HRB  /,N(36)/4HSR  /,N(37)/4HY   /,N(38)/4HZR  /,
     8N(39)/4HNB  /,N(40)/4HMO  /
      DATA N(41)/4HTC  /,N(42)/4HRU  /,N(43)/4HRH  /,N(44)/4HPD  /,N(45)
     1/4HAG  /,N(46)/4HCD  /,N(47)/4HIN  /,N(48)/4HSN  /,N(49)/4HSB  /,N
     2(50)/4HTE  /,N(51)/4HI   /,N(52)/4HXE  /,N(53)/4HCS  /,N(54)/4HBA 
     3 /,N(55)/4HLA  /,N(56)/4HCE  /,N(57)/4HPR  /,N(58)/4HND  /,N(59)/4
     4HPM  /,N(60)/4HSM  /,N(61)/4HEU  /,N(62)/4HGD  /,N(63)/4HTB  /,N(6
     54)/4HDY  /,N(65)/4HHO  /,N(66)/4HER  /,N(67)/4HTM  /,N(68)/4HYB  /
     6,N(69)/4HLU  /,N(70)/4HHF  /,N(71)/4HTA  /,N(72)/4HW   /,N(73)/4HR
     7E  /,N(74)/4HOS  /,N(75)/4HIR  /,N(76)/4HPT  /,N(77)/4HAU  /,N(78)
     8/4HHG  /,N(79)/4HTL  /,N(80)/4HPB  /
      DATA N(81)/4HBI  /,N(82)/4HPO  /,N(83)/4HAT  /,N(84)/4HRN  /,N(85)
     1/4HFR  /,N(86)/4HRA  /,N(87)/4HAC  /,N(88)/4HTH  /,N(89)/4HPA  /,N
     2(90)/4HU   /,N(91)/4HNP  /,N(92)/4HPU  /,N(93)/4HAM  /,N(94)/4HCM 
     3 /,N(95)/4HBK  /,N(96)/4HCF  /,N(97)/4HH   /,N(98)/4HD.  /
C-----IDENTIFY ELEMEN  FOR RETRIEVING NEUTRON SCATTERING LENGTH
      IF (KODLP.EQ.2) GO TO 3
C-----IDENTIFY WAVELENGTH
      DO 1 I=1,20
      IF (ANODE.EQ.M(I)) GO TO 2
 1    CONTINUE
      WRITE (IPR,14) ANODE
      GO TO 5
 2    IN=(FLOAT(I)-1.)/4.
C-----IDENTIFY ELEMENT SYMBOL
 3    DO 4 I=1,98
      IF (ELEMEN.EQ.N(I)) GO TO 6
 4    CONTINUE
      IF (KODLP.NE.2) WRITE (IPR,15) ELEMEN
 5    DELFR=0.
      DELFI=0.
      RETURN
 6    IF (KODLP.NE.2) GO TO 7
      CALL NEUTF (I,FNEU)
      RETURN
 7    IN=I+IN*96
	CONTINUE  !! READ(ID'IN)DELFR,DELFI
 13   RETURN
C
 14   FORMAT (13H THE ANODE **,A4,21H**  IS NOT RECOGNIZED /
     152H NO CORRECTION FOR ANOMALOUS DISPERSION WILL BE MADE)
 15   FORMAT (11H SYMBOL ***,A4,43H*** IS NOT ALLOWED FOR ANOMALOUS DISP
     1ERSION,/44H NO CORRECTION FOR THIS ELEMENT WILL BE MADE )
      END
      SUBROUTINE NEUTF (I,FNEU)
C-----CONTAINS THE NUCLEAR SCATTERING LENGTHS FOR THERMAL NEUTRONS
C-----COMPILED BY L. KOESTER IN "SPRINGER TRACTS IN MODERN PHYSICS NO 80
C----- NEUTRON PHYSICS, P 36 (1977) "
      DIMENSION A(98)
      DATA A(1)/-.203/,A(2)/.780/,A(3)/.535/,A(4)/.665/,A(5)/.936/,A(6)/
     1.580/,A(7)/.566/,A(8)/.460/,A(9)/.363/,A(10)/.538/,A(11)/.345/,A(1
     22)/.415/,A(13)/.513/,A(14)/.285/,A(15)/.958/,A(16)/.180/,A(17)/.37
     31/,A(18)/.490/,A(19)/1.215/,A(20)/-.337/,A(21)/-.041/,A(22)/.353/,
     4A(23)/-.373/,A(24)/.954/,A(25)/.278/,A(26)/1.030/,A(27)/.769/,A(28
     5)/.570/,A(29)/.720/,A(30)/.819/,A(31)/.673/,A(32)/.795/,A(33)/.677
     6/,A(34)/.791/,A(35)/.708/,A(36)/.688/,A(37)/.775/,A(38)/.700/,A(39
     7)/.711/,A(40)/.695/,A(41)/.680/,A(42)/.721/,A(43)/.588/,A(44)/.600
     8/,A(45)/.602/,A(46)/.380/,A(47)/.408/,A(48)/.622/,A(49)/.564/,A(50
     9)/.543/
      DATA A(51)/.528/,A(52)/.488/,A(53)/.542/,A(54)/.528/,A(55)/.827/,A
     1(56)/.483/,A(57)/.445/,A(58)/.780/,A(59)/.000/,A(60)/-.500/,A(61)/
     2.550/,A(62)/1.500/,A(63)/.738/,A(64)/1.710/,A(65)/.850/,A(66)/.803
     3/,A(67)/.705/,A(68)/1.262/,A(69)/.730/,A(70)/.777/,A(71)/.691/,A(7
     42)/.477/,A(73)/.920/,A(74)/1.080/,A(75)/1.060/,A(76)/.950/,A(77)/.
     5763/,A(78)/1.266/,A(79)/.889/,A(80)/.940/,A(81)/.853/,A(82)/.000/,
     6A(83)/.000/,A(84)/.000/,A(85)/.000/,A(86)/.000/,A(87)/.000/,A(88)/
     71.008/,A(89)/1.300/,A(90)/.861/,A(91)/1.060/,A(92)/.750/,A(93)/.76
     80/,A(94)/.700/,A(95)/.000/,A(96)/.000/,A(97)/-.374/,A(98)/.667/
      FNEU=A(I)
      RETURN
      END
      subroutine ahkl(NDBE,NHKL1,NHKL2)
C-----******************************************************************
      DOUBLE PRECISION PI2
      character*20 file
      character*24 tmp
      logical qex
      INTEGER NORM
      REAL ITIT,JB,IDL,IWL,ILP
      DIMENSION  Q(8000), IYH(8000), IYK(8000), IYL(8000),NA(8),
     1COMPND(19),NT(36),IY(8000),IORD(8000),THETA(8000)
      DIMENSION ITIT(13),JB(21),IDT(9),IDL(25),IPH(5),IPK(5),IPL(5),
     *MIT(5)
      COMMON /UNITS/ IPR
      COMMON /EQUO/ TS(3,24),FS(3,3,24),NS,ISYMCE,IBRAVL
      DATA ITIT(1)/4H FOL/,ITIT(2)/4HLOWS/,ITIT(3)/4H OMI/,ITIT(4)/4HTTE
     1D/,ITIT(5)/3H MM/,ITIT(6)/3H   /,ITIT(7)/3H2TH/,ITIT(8)/3HETA/,ITI
     2T(9)/4H NOT/,ITIT(10)/4HLOW /,ITIT(11)/4HHIGH/,ITIT(12)/2HNO/,ITIT
     3(13)/2H A/
      DATA JB(1)/4HPRIM/,JB(2)/4HITIV/,JB(3)/4HE   /,JB(4)/4HBODY/,JB(5)
     1/4H CEN/,JB(6)/4HTRED/,JB(7)/4HRHOM/,JB(8)/4HBOHE/,JB(9)/4HDRAL/,J
     2B(10)/4HFACE/,JB(11)/4H CEN/,JB(12)/4HTRED/,JB(13)/4HA -C/,JB(14)/
     34HENTR/,JB(15)/4HED  /,JB(16)/4HB -C/,JB(17)/4HENTR/,JB(18)/4HED  
     4/,JB(19)/4HC -C/,JB(20)/4HENTR/,JB(21)/4HED  /
      DATA IDL(1)/4H DEB/,IDL(2)/4HYE S/,IDL(3)/4HCHER/,IDL(4)/4HRER /,I
     1DL(5)/4H    /,IDL(6)/4HSPEC/,IDL(7)/4HIAL /,IDL(8)/4HWITH/,IDL(9)/
     24H LP=/,IDL(10)/4H1   /,IDL(11)/4H NEU/,IDL(12)/4HTRON/,IDL(13)/4H
     3 DIF/,IDL(14)/4HFRAC/,IDL(15)/4HTION/,IDL(16)/4H    /,IDL(17)/4H G
     4UI/,IDL(18)/4HNIER/,IDL(19)/4H CAM/,IDL(20)/4HERA /,IDL(21)/4H GUI
     5/,IDL(22)/4HNIER/,IDL(23)/4H CAM/,IDL(24)/4HERA /,IDL(25)/4H    /
C-----
C-----CHANGE THE FOLLOWING PARAMETERS IF NECESSARY
C-----
      IPR=35
      ILU=29
      LIMIT1=8000
      LIMIT2=1
      LIMIT3=1
      LIMIT4=24
      DG1=3.343
      DG2=3.343
      DM1=114.59156
      DM2=100.
      BG1=30.
      BG2=30.
	ITP=1
      OPEN(UNIT=ILU,FILE='LAZY.LAZ',STATUS='OLD',FORM='UNFORMATTED')
	READ(ILU)NCHR,FILE
        lfile=len(FILE)
        do while (FILE(lfile:lfile).eq.' ')
        lfile=lfile-1
        enddo
      tmp=FILE(1:lfile)//'.imp'
      inquire(file=tmp,exist=qex)
      if(qex.eq..FALSE.)go to 800
      call filedel(IPR,tmp)
800   call open_write1(IPR,tmp)
C-----
C-----END OF PARAMETERS
C-----
	WRITE(IPR,1711)FICHE
1711	FORMAT(1X,A20)
      NFI=0
      PI2=6.283185307179586D0
      E=2.7182818
      FRTD=4./3.
C-----READ INPUT FROM BINARY DATA FILE ILU
C-----READ NUMBER OF FILES ON ILU
      READ (ILU) NFIL
 1    NFI=NFI+1
      WRITE (IPR,141)
      IF (NFI.LE.NFIL) GO TO 2
      WRITE (IPR,139)
      GO TO 137
 2    READ (ILU) (COMPND(I),I=1,19),A,B,C,ALPHA,BETA,GAMMA,WL,(NT(I),I=1
     1,36),IGROUP, IWL, ILP
      IF (A.GT.0.) GO TO 3
      WRITE (IPR,140) NFI
      GO TO 1
 3    READ (ILU) ISYSTM,ISYMCE,IBRAVL,NS,TL,TH,NORM,IMAGE,ANO,KODLP,NCOM
     1PO,(NA(I),I=1,8),IHOO,IOKO,IOOL,IHHL,IHOL,IHKO,IOKL,LAUE
      IF (NS.GT.LIMIT4) GO TO 136
	IF(NCOMPO.GT.LIMIT2)GOTO 134
      READ (ILU) ((TS(I,II),(FS(K,I,II),K=1,3),I=1,3),II=1,NS)
C-----SET VARIABLES BACK TO ORIGINAL VALUE
C-----PRINT FIRST LINE OF TITLE
      VMXINT=0
      NLINE=0
	J1=1
      N=0
      ICON=0
      DUM=1.
      FBRA=IBRAVL
      IF (FBRA.GT.4.) FBRA=2.
C-----MULTIPLIER IF CENTER OF SYMMETRY AT ORIGIN
      IF (ISYMCE.NE.0) DUM=2.
C-----CALCULATE SIN**2 THETA LIMITS
      SH=TH*PI2/360.
      SL=TL*PI2/360.
      SH=(SIN(SH))**2
      SL=(SIN(SL))**2
C	print 502
C502	FORMAT('  REFLECTIONS DOUBLED (with alpha-2) ? YES=2,NO=1'$)
C	read *,NDBE
C	IF(NDBE.EQ.2)GO TO 506
C	print 504
C504	FORMAT('  CODE FOR REFLECTIONS ? '$)
C	read *,NHKL1
C	GO TO 508
506   CONTINUE
C506	print 505
C505	FORMAT('  2 CODES FOR REFLECTIONS (4 and 5 for X-rays) ? '$)
C	read *,NHKL1,NHKL2
C-----PRINT TITLE
508      WRITE (IPR,165) COMPND
      WLSQ4=WL**2/4.
      ASTAR=WLSQ4/A**2
      IF ((ISYSTM.EQ.1).OR.(ISYSTM.EQ.2).OR.(ISYSTM.EQ.7)) BSTAR=WLSQ4/B
     1**2
      IF (ISYSTM.NE.5) CSTAR=WLSQ4/C**2
      BET=BETA*PI2/360.
      SINB2=(SIN(BET))**2
      COSB=COS(BET)
C-----TRICLINIC CASE
      IF (ISYSTM.NE.7) GO TO 8
      ALPH=ALPHA*PI2/360.
      GAMM=GAMMA*PI2/360.
      SV=(ALPH+BET+GAMM)/2.
      VOL=2.*A*B*C*SQRT(SIN(SV)*SIN(SV-ALPH)*SIN(SV-BET)*SIN(SV-GAMM))
      AST=(B*C*SIN(ALPH))/VOL
      BST=(A*C*SIN(BET))/VOL
      CST=(A*B*SIN(GAMM))/VOL
      COAST=(COSB*COS(GAMM)-COS(ALPH))/(SIN(BET)*SIN(GAMM))
      COBST=(COS(GAMM)*COS(ALPH)-COSB)/(SIN(GAMM)*SIN(ALPH))
      COGST=(COS(ALPH)*COSB-COS(GAMM))/(SIN(ALPH)*SIN(BET))
C-----START LOOP TO FIND HKL LIMITS FOR GIVEN SL AND SH LIMITS
520	ICON=0
 8    ZH=0.
      ZK=0.
      ZL=0.
 9    ZH=ZH+1.0
      GO TO (10,15,16,21,22,23,24), ISYSTM
C-----MONOCLINIC
 10   ZHTEST=(2.0*A*SQRT(SH))/WL
      IF (ZH.LE.ZHTEST) GO TO 13
      ZH=0.
      ZK=ZK+1.
      ZKTEST=(2.0*B*SQRT(SH))/WL
      IF (ZK.LE.ZKTEST) GO TO 10
      ZK=0.
      IF (ICON.EQ.0) GO TO 11
      ZL=ZL-1.
      GO TO 12
 11   ZL=ZL+1.
 12   ZLTEST=(2.0*C*SQRT(SH))/WL
      IF (ABS(ZL).LE.ZLTEST) GO TO 10
      IF (ICON.EQ.1) GO TO 14
      ICON=1
      GO TO 8
 13   ATEST=ASTAR*ZH**2/SINB2+BSTAR*ZK**2+CSTAR*ZL**2/SINB2-WLSQ4*2.*ZH*
     1ZL*COSB/(A*C*SINB2)
      IF (ATEST.GT.SH) GO TO 9
      IF ((ICON.EQ.0).OR.((ZH.GT.0.9).AND.(ZL.LT.(-0.9)))) GO TO 31
      GO TO 9
 14   IF(ITP.EQ.0)GO TO 521
	WRITE (IPR,187)
      WRITE (IPR,168) A,B,C,BETA,WL
521      GO TO 73
C-----ORTHORHOMBIC
 15   ATEST=ASTAR*ZH**2+BSTAR*ZK**2+CSTAR*ZL**2
      IF (ATEST.LE.SH) GO TO 31
      ZH=0.
      ZK=ZK+1.
      BTEST=BSTAR*ZK**2+CSTAR*ZL**2
      IF (BTEST.LE.SH) GO TO 15
      ZK=0.
      ZL=ZL+1.
      CTEST=CSTAR*ZL**2
      IF (CTEST.LE.SH) GO TO 15
	IF(ITP.EQ.0)GO TO 522
      WRITE (IPR,189)
      WRITE (IPR,169) A,B,C,WL
522      GO TO 73
C-----TRIGONAL
 16   ATEST=FRTD*ASTAR*(ZH**2+ZH*ZK+ZK**2)+CSTAR*ZL**2
      IF ((ZH.EQ.0.).AND.(ZL.EQ.0.)) GO TO 9
      IF (ATEST.LE.SH) GO TO 19
      ZH=0.
      ZK=ZK+1.
      BTEST=FRTD*ASTAR*ZK**2+CSTAR*ZL**2
      IF (BTEST.LE.SH) GO TO 16
      ZK=0.
      IF (ICON.EQ.0) GO TO 17
      ZL=ZL-1.
      GO TO 18
 17   ZL=ZL+1.
 18   CTEST=CSTAR*ZL**2
      IF (CTEST.LE.SH) GO TO 16
      IF (ICON.EQ.1) GO TO 20
      ICON=1
      GO TO 8
 19   IF ((ICON.EQ.0).OR.((ZL.LT.(-0.9)).AND.((ZH.NE.0.).AND.(ZK.NE.0.))
     1)) GO TO 31
      GO TO 9
 20   IF(ITP.EQ.0)GO TO 523
	WRITE (IPR,190)
523      GO TO 72
C-----TETRAGONAL
 21   ATEST=ASTAR*(ZH**2+ZK**2)+CSTAR*ZL**2
      IF (ATEST.LE.SH) GO TO 31
      ZH=ZK+1.
      ZK=ZH
      BTEST=ASTAR*2.*ZH**2+CSTAR*ZL**2
      IF (BTEST.LE.SH) GO TO 21
      ZH=0.
      ZK=0.
      ZL=ZL+1.
      CTEST=CSTAR*ZL**2
      IF (CTEST.LE.SH) GO TO 21
	IF(ITP.EQ.0)GO TO 524
      WRITE (IPR,191)
524      GO TO 72
C-----CUBIC
 22   ATEST=ASTAR*(ZH**2+ZK**2+ZL**2)
      IF (ATEST.LE.SH) GO TO 31
      ZH=ZK+1.
      ZK=ZH
      BTEST=ASTAR*(2.*ZH**2+ZL**2)
      IF (BTEST.LE.SH) GO TO 22
      ZH=ZL+1.
      ZK=ZH
      ZL=ZH
      CTEST=ASTAR*3.*ZH**2
      IF (CTEST.LE.SH) GO TO 22
	IF(ITP.EQ.0)GO TO 525
      WRITE (IPR,192)
      WRITE (IPR,171) A,WL
525      GO TO 73
C-----HEXAGONAL
 23   ATEST=FRTD*ASTAR*(ZH**2+ZH*ZK+ZK**2)+CSTAR*ZL**2
      IF (ATEST.LE.SH) GO TO 31
      ZH=ZK+1.
      ZK=ZH
      BTEST=FRTD*ASTAR*3.*ZH**2+CSTAR*ZL**2
      IF (BTEST.LE.SH) GO TO 23
      ZH=0.
      ZK=0.
      ZL=ZL+1.
      CTEST=CSTAR*ZL**2
      IF (CTEST.LE.SH) GO TO 23
	IF(ITP.EQ.0)GO TO 526
      WRITE (IPR,193)
526      GO TO 72
C-----TRICLINIC
 24   ZHTEST=(2.0*A*SQRT(SH))/WL
      IF (ZH.LE.ZHTEST) GO TO 29
      ZH=0.
      IF (ICON.LT.2) GO TO 25
      ZK=ZK-1.
      GO TO 26
 25   ZK=ZK+1.
 26   ZKTEST=(2.0*B*SQRT(SH))/WL
      IF (ABS(ZK).LE.ZKTEST) GO TO 24
      ZK=0.
      IF ((ICON.EQ.0).OR.(ICON.EQ.2)) GO TO 27
      ZL=ZL-1.
      GO TO 28
 27   ZL=ZL+1.
 28   ZLTEST=(2.0*C*SQRT(SH))/WL
      IF (ABS(ZL).LE.ZLTEST) GO TO 24
      ICON=ICON+1
      GO TO (8,8,8,30), ICON
 29   ATEST=WLSQ4*((ZH*AST)**2+(ZK*BST)**2+(ZL*CST)**2+2.*ZK*ZL*BST*CST*
     1COAST+2.*ZH*ZL*AST*CST*COBST+2.*ZH*ZK*AST*BST*COGST)
      IF (ATEST.GT.SH) GO TO 9
      IF (ICON.EQ.0) GO TO 31
      IF (((ZH.EQ.0.).AND.(ZK.EQ.0.)).OR.((ZK.EQ.0.).AND.(ZL.EQ.0.)).OR.
     1((ZH.EQ.0.).AND.(ZL.EQ.0.))) GO TO 9
      IF ((ICON.EQ.1).AND.(ZL.LT.(-0.9))) GO TO 31
      IF (((ICON.EQ.2).AND.(ZK.LT.(-0.9))).AND.(ZH.GT.0.9)) GO TO 31
      IF ((ICON.EQ.3).AND.((ZH*ZK*ZL).NE.0.)) GO TO 31
      GO TO 9
C-----PRINT TRICLINIC LATTICE CONSTANTS
 30   IF(ITP.EQ.0)GO TO 527
	WRITE (IPR,188)
      WRITE (IPR,172) A,B,C,ALPHA,BETA,GAMMA,WL
527      GO TO 73
 31   IF (ATEST.LE.SL) GO TO 9
      XH=ZH
      XK=ZK
      XL=ZL
C-----OMIT HKL VALUES CORRESPONDING TO BRAVAIS LATTICE EXTINCTIONS
 32   GO TO (40,33,34,35,36,37,38), IBRAVL
 33   TESTBR=(XH+XK+XL)/2.
      GO TO 39
 34   TESTBR=(-XH+XK+XL)/3.
      GO TO 39
 35   FACEHK=(XH+XK)/2.
      IF ((AINT(FACEHK)-FACEHK).NE.0.) GO TO 9
 36   TESTBR=(XK+XL)/2.
      GO TO 39
 37   TESTBR=(XH+XL)/2.
      GO TO 39
 38   TESTBR=(XH+XK)/2.
 39   IF ((AINT(TESTBR)-TESTBR).NE.0.) GO TO 68
C-----OMIT HKL VALUES CORRESPONDING TO EXTINCTIONS
 40   IF (XL.EQ.0.) GO TO (41,50,49,50,47), IHKO
 41   IF (XH.EQ.0.) GO TO (42,54,53,54,51), IOKL
 42   IF (XK.EQ.0.) GO TO (43,58,57,58,55), IHOL
 43   IF (XH.EQ.XK) GO TO (44,59,61), IHHL
      IF ((XK.EQ.XL).AND.(ISYSTM.EQ.5)) GO TO (44,62,44,63), IHHL
 44   IF (XK.EQ.0..AND.XL.EQ.0.) GO TO (45,64,133,64), IHOO
 45   IF (XH.EQ.0..AND.XL.EQ.0.) GO TO (46,65,133,65), IOKO
 46   IF (XH.EQ.0..AND.XK.EQ.0.) GO TO (67,66,66,66,133,66), IOOL
      GO TO 67
 47   FIHKO=XH/2.
 48   IF (AINT(FIHKO)-FIHKO) 68,41,68
 49   FIHKO=XK/2.
      GO TO 48
 50   HKO=IHKO
      FIHKO=(XH+XK)/HKO
      GO TO 48
 51   FIOKL=XK/2.
 52   IF (AINT(FIOKL)-FIOKL) 68,42,68
 53   FIOKL=XL/2.
      GO TO 52
 54   OKL=IOKL
      FIOKL=(XK+XL)/OKL
      GO TO 52
 55   FIHOL=XH/2.
 56   IF (AINT(FIHOL)-FIHOL) 68,43,68
 57   FIHOL=XL/2.
      GO TO 56
 58   HOL=IHOL
      FIHOL=(XH+XL)/HOL
      GO TO 56
 59   FIHHL=XL/2.
 60   IF (AINT(FIHHL)-FIHHL) 68,44,68
 61   FIHHL=(2.*XH+XL)/4.
      GO TO 60
 62   FIHHL=XH/2.
      GO TO 60
 63   FIHHL=(2.*XL+XH)/4.
      GO TO 60
 64   HOO=IHOO
      FIHOO=XH/HOO
      IF (AINT(FIHOO)-FIHOO) 68,45,68
 65   FIOKO=XK/2.
      IF (AINT(FIOKO)-FIOKO) 68,46,68
 66   OOL=IOOL
      FIOOL=XL/OOL
      IF ((AINT(FIOOL)-FIOOL).NE.0.) GO TO 68
C-----STORE HKL AND SIN2THETA VALUES OF F VALUES  TO BE CALCULATED
 67   N=N+1
C-----CHECK IF NUMBER OF REFLECTIONS TOO LARGE
      IF (N.GT.LIMIT1) GO TO 501
      Q(N)=ATEST
      IF(XH.GE.0.)IYH(N)=XH+0.5
      IF(XK.GE.0.)IYK(N)=XK+0.5
      IF(XL.GE.0.)IYL(N)=XL+0.5
	IF(XH.LT.0.)IYH(N)=XH-0.5
	IF(XK.LT.0.)IYK(N)=XK-0.5
	IF(XL.LT.0.)IYL(N)=XL-0.5
      JJ=N
      J=JJ-1
C-----SKIP REFLECTIONS RELATED BY LAUE SYMMETRY
 68   IF ((LAUE.EQ.2).OR.(ZH.EQ.XK)) GO TO 9
      GO TO (9,9,9,69,70,69,9), ISYSTM
 69   IF ((ZH.GT.ZK).AND.(ZK.GT.0.)) GO TO 71
      GO TO 9
 70   IF ((ZH.GT.ZK).AND.(ZK.GT.ZL)) GO TO 71
      GO TO 9
 71   TEMP=XH
      XH=XK
      XK=TEMP
      GO TO 32
C-----PRINT HEX AND TETRAG LATTICE CONSTANTS, END OF HKL GENER.LOOP
 72   IF(ITP.EQ.0)GO TO 73
	WRITE (IPR,170) A,C,WL
 73   MP=KODLP*5+1
      KK=MP+4
      WRITE (IPR,173) TL,TH,(IDL(I),I=MP,KK)
C-----CHECK IF NUMBER OF REFLECTIONS TOO LARGE
      IF(N.GT.LIMIT1) GO TO 501
C-----PRINT SPACE GROUP AND EQUIVALENT POSITIONS
      NN=6
      IF (IGROUP.EQ.0) NN=9
	IF(ITP.EQ.0)GO TO 528
      WRITE (IPR,144) ITIT(NN),(NT(I),I=1,36)
      CALL EQUI
C-----PRINT LAUE SYMMETRY
528      IF (ISYSTM.LT.3) GO TO 74
      NN=10
      IF (LAUE.EQ.2) NN=11
	IF(ITP.EQ.0)GO TO 74
      WRITE (IPR,145) ITIT(NN)
 74   NN=12
C-----PRINT SYMMETRY CENTER
      IF (ISYMCE.EQ.1) NN=13
	IF(ITP.EQ.0)GO TO 529
      WRITE (IPR,146) ITIT(NN)
C-----PRINT BRAVAIS LATTICE AND EXTINCTIONS
      NN=IBRAVL*3-2
      WRITE (IPR,147) JB(NN),JB(NN+1),JB(NN+2)
      WRITE (IPR,148)
      IF(IBRAVL.EQ.1) WRITE(IPR,208)
      IF(IBRAVL.EQ.2) WRITE(IPR,213)
      IF(IBRAVL.EQ.3) WRITE(IPR,214)
      IF(IBRAVL.EQ.4) WRITE(IPR,212)
      IF(IBRAVL.EQ.5) WRITE(IPR,209)
      IF(IBRAVL.EQ.6) WRITE(IPR,215)
      IF(IBRAVL.EQ.7) WRITE(IPR,211)
      IF ((IHKO.EQ.2).OR.(IHKO.EQ.4)) WRITE (IPR,176) IHKO
      IF (IHKO.EQ.3) WRITE (IPR,175)
      IF (IHKO.EQ.5) WRITE (IPR,174)
      IF ((IOKL.EQ.2).OR.(IOKL.EQ.4)) WRITE (IPR,178) IOKL
      IF (IOKL.EQ.3) WRITE (IPR,210)
      IF (IOKL.EQ.5) WRITE (IPR,177)
      IF ((IHOL.EQ.2).OR.(IHOL.EQ.4)) WRITE (IPR,181) IHOL
      IF (IHOL.EQ.3) WRITE (IPR,180)
      IF (IHOL.EQ.5) WRITE (IPR,179)
      IF (IHHL.EQ.2) WRITE (IPR,182)
      IF (IHHL.EQ.3) WRITE (IPR,183)
      IF (IHOO.GT.1) WRITE (IPR,184) IHOO
      IF (IOKO.GT.1) WRITE (IPR,185) IOKO
      IF (IOOL.GT.1) WRITE (IPR,186) IOOL
C-----EXIT IF NUMBER OF REFLECTIONS LESS THAN TWO
529      IF(J.LE.1) GO TO 206
C-----START ORDERING REFLEXIONS
	DO 406 NN=J1,JJ
406	IORD(NN)=NN
      DO 81 NN=J1,J
      NNN=NN+1
      DO 81 M=NNN,JJ
      IF ((Q(NN)-Q(M)).LE.0.) GO TO 81
	TEMP=Q(NN)
	Q(NN)=Q(M)
	Q(M)=TEMP
	ITEMP=IORD(NN)
	IORD(NN)=IORD(M)
	IORD(M)=ITEMP
81	CONTINUE
	DO 400 NN=J1,JJ
400	IY(NN)=IYH(IORD(NN))
	DO 401 NN=J1,JJ
401	IYH(NN)=IY(NN)
	DO 402 NN=J1,JJ
402	IY(NN)=IYK(IORD(NN))
	DO 403 NN=J1,JJ
403	IYK(NN)=IY(NN)
	DO 404 NN=J1,JJ
404	IY(NN)=IYL(IORD(NN))
	DO 405 NN=J1,JJ
405	IYL(NN)=IY(NN)
C	print 503,JJ
503	FORMAT('  NBRE HKL =',I5)
	J1=JJ+1
	JJ1=JJ
	ITP=0
501	IF(N.GT.LIMIT1)WRITE(IPR,195)LIMIT1
C-----END OF ORDERING
C-----START LOOP TO CALCULATE F FOR ALL STORED REFLEXIONS
	JJ21=JJ1
	IF(NDBE.EQ.2)JJ21=JJ21*2
	WRITE(21,1214)JJ21
	PRINT 1214,JJ21
 1214 FORMAT(' TOTAL NUMBER OF HKL : ',I5)
	WRITE(21,1213)
 1213 FORMAT('    H   K   L  MULT   d(A)    2-theta(°)')
	IP1=0
      DO 107 N=1,JJ1
	THETA(N)=57.29578*ATAN(SQRT(Q(N)/(1.-Q(N))))
C-----CALCULATE MULTIPLICITY FOR POWDERLINE
      GO TO (82,84,87,89,91,93,96), ISYSTM
 82   IF ((IYK(N).EQ.0).OR.((IYH(N).EQ.0).AND.(IYL(N).EQ.0))) GO TO 96
 83   FMULTI=4.0
      GO TO 98
 84   IF (IYH(N).EQ.0) IF (IYK(N)) 133,96,86
      IF (IYK(N).EQ.0) GO TO 86
      IF (IYL(N).EQ.0) GO TO 83
 85   FMULTI=8.0
      GO TO 98
 86   IF (IYL(N)) 133,96,83
 87   IF ((IYH(N).EQ.0).AND.(IYK(N).EQ.0)) GO TO 96
 88   FMULTI=6.0
      GO TO 98
 89   IF ((IYH(N)-IYK(N)).EQ.0) IF (IYH(N)) 133,96,90
      IF (IYK(N).EQ.0) GO TO 90
      IF (IYL(N).EQ.0) IF (LAUE-1) 133,83,85
      IF (LAUE.EQ.1) GO TO 85
      FMULTI=16.
      GO TO 98
 90   IF (IYL(N)) 133,83,85
 91   IF ((IYH(N)-IYK(N)).EQ.0) IF (IYL(N)) 133,97,92
      IF ((IYL(N).EQ.0).AND.(LAUE.EQ.2)) IF (IYK(N)) 133,88,94
      IF ((IYL(N).EQ.0).AND.(LAUE.EQ.1)) IF (IYK(N)) 133,88,97
      IF (((IYK(N)-IYL(N)).EQ.0).OR.(LAUE.EQ.1)) GO TO 94
      FMULTI=48.
      GO TO 98
 92   IF (IYH(N)-IYL(N)) 133,85,94
 93   IF ((IYH(N)-IYK(N)).EQ.0) IF (IYH(N)) 133,96,95
      IF (IYK(N).EQ.0) GO TO 95
      IF ((IYL(N).EQ.0).AND.(LAUE.EQ.1)) GO TO 88
      IF ((IYL(N).EQ.0).OR.(LAUE.EQ.1)) GO TO 97
 94   FMULTI=24.0
      GO TO 98
 95   IF (IYL(N)) 133,88,97
 96   FMULTI=2.0
      GO TO 98
 97   FMULTI=12.0
98	IP1=IP1+1
	IPH(1)=IYH(N)
	IPK(1)=IYK(N)
	IPL(1)=IYL(N)
	MIT(1)=FMULTI
C
      DVAL=WL/(2.*SQRT(Q(N)))
      THETA2=2.*THETA(N)  
C                                
	WRITE(21,1212)IPH(1),IPK(1),IPL(1),MIT(1),DVAL,THETA2
C	IF(NDBE.EQ.2)WRITE(36,1212)NHKL2,IPH(1),IPK(1),IPL(1),MIT(1)
	IP1=0
1212	FORMAT(1X,4I4,F10.4,F10.3)
C-----END OF LOOP TO CALCULATE F FOR ALL STORED AND ORDERED HKL VALUES
 107  CONTINUE
	IF(MOD(JJ1,5).EQ.0)GOTO 1071
C	WRITE(36,1212)(IPH(IP2),IPK(IP2),IPL(IP2),MIT(IP2),IP2=1,IP1)
1071	CONTINUE
	WRITE(IPR,1631)STIM
1631	FORMAT(//1X,'Fin d execution : ',8A1)
      GO TO 1
 133  WRITE (IPR,194)
      GO TO 1
134	WRITE(IPR,162)
	GOTO 1
  136  WRITE (IPR,164) NS
      GO TO 1
206	WRITE(IPR,207)
	GOTO 1
 137  return
C-----
 139  FORMAT (/39H B Y E  B Y E  L A Z Y  P U L V E R I X  )
 140  FORMAT (4H JOB  ,I5,40H IS BAD DUE TO ERROR IN PREVIOUS PROGRAM,/1
     16H GO TO NEXT JOB ,//)
 141  FORMAT (2X,'Date : ',9A1,5X,'Heure : ',8A1,5X,'*** PULVERIX ***'/)
 144  FORMAT ( /12H SPACE GROUP,A4,22H GIVEN ON SPCGRP-CARD ,36A1)
 145  FORMAT (/1X,A4,14H LAUE SYMMETRY)
 146  FORMAT (/10H THERE IS ,A2,30H SYMMETRY CENTRE AT THE ORIGIN)
 147  FORMAT (/1X,3A4,16H BRAVAIS LATTICE)
 148  FORMAT ( /41H CONDITIONS LIMITING POSSIBLE REFLECTIONS  /)
 156  FORMAT (/// 1X,50(1H-),//41H - T A B U L A R  L I S T  OF INTENSIT
     1IES,2A4,2H -//1X,50(1H-))
 162  FORMAT(1X,'NOMBRE DE SORTES D ATOMES TROP GRAND'//)
 164  FORMAT(1X,'NOMBRE D EQUIVALENTS SYMETRIQUES TROP GRAND '///)
 165  FORMAT (/27H INTENSITY CALCULATION FOR ,19A4/)
 168  FORMAT(3H A=,F9.5/3H B=,F9.5/3H C=,F9.5/6H BETA=,F9.5/4H WL=,F8.5)
 169  FORMAT (3H A=,F9.5/3H B=,F9.5/3H C=,F9.5/4H WL=,F8.5/)
 170  FORMAT (3H A=,F9.5/3H C=,F9.5/4H WL=,F8.5)
 171  FORMAT (3H A=,F9.5/4H WL=,F8.5)
 172  FORMAT (3H A=,F9.5/3H B=,F9.5/3H C=,F9.5/7H ALPHA=,F9.5/6H BETA=,
     1F9.5/7H GAMMA=,F9.5/4H WL=,F8.5)
 173  FORMAT(/26H CALCULATION BETWEEN TL = ,F4.1,9H AND TH =,F6.1,
     116H DEGREES THETA  ,//23H DIFFRACTION GEOMETRY =,5A4)
 174  FORMAT (19H HKO WITH H=2N ONLY)
 175  FORMAT (19H HKO WITH K=2N ONLY)
 176  FORMAT (14H HKO WITH H+K=,I1,6HN ONLY)
 177  FORMAT (19H OKL WITH K=2N ONLY)
 210  FORMAT (19H OKL WITH L=2N ONLY)
 178  FORMAT (14H OKL WITH K+L=,I1,6HN ONLY)
 179  FORMAT (19H HOL WITH H=2N ONLY)
 180  FORMAT (19H HOL WITH L=2N ONLY)
 181  FORMAT (14H HOL WITH H+L=,I1,6HN ONLY)
 182  FORMAT (19H HHL WITH L=2N ONLY)
 183  FORMAT (22H HHL WITH 2H+L=4N ONLY)
 184  FORMAT (12H HOO WITH H=,I1,6HN ONLY)
 185  FORMAT (12H OKO WITH K=,I1,6HN ONLY)
 186  FORMAT (12H OOL WITH L=,I1,6HN ONLY)
 187  FORMAT (/21H MONOCLINIC STRUCTURE)
 188  FORMAT (/20H TRICLINIC STRUCTURE)
 189  FORMAT (/23H ORTHORHOMBIC STRUCTURE)
 190  FORMAT (/19H TRIGONAL STRUCTURE)
 191  FORMAT (/21H TETRAGONAL STRUCTURE)
 192  FORMAT (/16H CUBIC STRUCTURE)
 193  FORMAT (/20H HEXAGONAL STRUCTURE)
 194  FORMAT(/53H SOMETHING VERY BAD HAPPENED. CALL THE AUTHORS PLEASE)
 195  FORMAT (/11H *OVERFLOW*,/38H NUMBER OF REFLECTIONS IS GREATER THAN
     1,I5)
  200  FORMAT (1H1,131H H  K  L THETA  MM     D     SIN2   H  K  L INTENS
     1    F+(HKL)    F-(HKL)  A+(HKL)  A-(HKL)  B+(HKL)  B-(HKL) PHA+  P
     2HA- MULT   LPG /)
 201  FORMAT(/130H1 H  K  L    THETA  SIN2*1000 INT.SCALED   INTENSITY U
     1NSCALED           /F(HKL)/        A(HKL)        B(HKL) PHA.ANG. MU
     2LT    LPG   /)
 202  FORMAT(/18H1 H  K  L  THETA  ,2A3,107H D VALUE  1/D**2 SIN2*1000  
     1H  K  L INTENSITY         /F(HKL)/       A(HKL)      B(HKL) PHA.AN
     2G. MULT   LPG  /)
 207  FORMAT(1X,'MOINS DE DEUX REFLECTIONS DANS L ESPACE DEFINI !!!!'//)
  208  FORMAT(10H HKL  NONE)
 209  FORMAT(21H HKL WITH K+L=2N ONLY)
 215  FORMAT(21H HKL WITH H+L=2N ONLY)
 211  FORMAT(21H HKL WITH H+K=2N ONLY)
 212  FORMAT(40H HKL WITH H,K,L ALL EVEN OR ALL ODD ONLY )
 213  FORMAT(23H HKL WITH H+K+L=2N ONLY)
 214  FORMAT(24H HKL WITH -H+K+L=3N ONLY)
      END
      SUBROUTINE EQUI
C-----PRINTS EQUIPOINTS STORED IN TS,FS,ISYMCE AND IBRAVL
	REAL IB,N3
      COMMON /EQUO/ TS,FS,NG,ISYMCE,IBRAVL
      COMMON /UNITS/ NPT
      DIMENSION TS(3,24), FS(3,3,24), CON1(7), SYMB1(8), SYMB2(9), DIG(1
     13), IB(24), IP(12), N3(9)
      DATA IB(1)/4H1/2 /,IB(2)/4H2/3 /,IB(3)/4H1/2 /,IB(4)/4H 0  /,IB(5)
     1/4H1/2 /,IB(6)/4H1/2 /,IB(7)/4H1/2 /,IB(8)/4H1/3 /,IB(9)/4H1/2 /,I
     2B(10)/4H1/2 /,IB(11)/4H 0  /,IB(12)/4H1/2 /,IB(13)/4H1/2)/,IB(14)/
     34H1/3 /,IB(15)/4H 0, /,IB(16)/4H1/2)/,IB(17)/4H1/2)/,IB(18)/4H 0 )
     4/,IB(19)/4H1/3 /,IB(20)/4H1/2 /,IB(21)/4H2/3 /,IB(22)/4H 0  /,IB(2
     53)/4H2/3)/,IB(24)/4H1/2,/
      DATA CON1(1)/0.75/,CON1(2)/0.6667/,CON1(3)/0.5/,CON1(4)/0.3333/,CO
     1N1(5)/0.25/,CON1(6)/0.16667/,CON1(7)/0.83333/
      DATA SYMB1(1)/3H3/4/,SYMB1(2)/3H2/3/,SYMB1(3)/3H1/2/,SYMB1(4)/3H1/
     13/,SYMB1(5)/3H1/4/,SYMB1(6)/3H1/6/,SYMB1(7)/3H5/6/,SYMB1(8)/3H   /
      DATA SYMB2(1)/3H +X/,SYMB2(2)/3H  X/,SYMB2(3)/3H -X/,SYMB2(4)/3H +
     1Y/,SYMB2(5)/3H  Y/,SYMB2(6)/3H -Y/,SYMB2(7)/3H +Z/,SYMB2(8)/3H  Z/
     2,SYMB2(9)/3H -Z/
      DATA N3(1)/1H /,N3(2)/3H   /,N3(3)/4H    /,N3(4)/1H,/,N3(5)/4H+(0 
     1/,N3(6)/4H0 0,/,N3(7)/4H 0  /,N3(8)/4H1/2 /,N3(9)/4H1/2)/
      WRITE (NPT,15)
      DIG(13)=N3(1)
      IF (ISYMCE.EQ.1) DIG(13)=N3(4)
C-----FILL OUTPUT STRING WITH BLANKS
      DO 1 NN=1,12
      IP(NN)=N3(3)
 1    DIG(NN)=SYMB1(8)
C-----FILL OUTPUT STRING IP WITH BRAVAIS LATTICE VECTORS
      IF (IBRAVL.LT.2) GO TO 4
C-----FIRST VECTOR
      IP(1)=N3(5)
      IP(2)=N3(6)
C-----SECOND VECTOR
      DO 2 I=1,3
      I1=I+2
      I2=IBRAVL-1
      I3=I*6-6
 2    IP(I1)=IB(I2+I3)
      IF ((IBRAVL.LT.3).OR.(IBRAVL.GT.4)) GO TO 4
C-----THIRD VECTOR
      I2=16+IBRAVL
      DO 3 I=1,3
      I1=I+5
      I3=I*2-2
 3    IP(I1)=IB(I2+I3)
C-----FORTH VECTOR
      IF (IBRAVL.EQ.3) GO TO 4
      IP(9)=N3(7)
      IP(10)=N3(8)
      IP(11)=N3(9)
C-----LOOP OVER NUMBER OF EQUIPOINTS
 4    DO 14 I=1,NG
C-----FILL OUTPUT STRING WITH BLANKS
      DO 5 NN=1,12
 5    DIG(NN)=N3(2)
      ANTI=1.
      NN=1
C-----LOOP OVER X Y Z  COORDINATES
 6    DO 12 J=1,3
      TS1=ANTI*TS(J,I)
      IF (TS1.LT.0.) TS1=1.+TS1
      N1=1
      IF (TS1.EQ.0.) GO TO 9
      DO 7 II=1,7
      DIF=TS1-CON1(II)
      DIF=ABS(DIF)
      IF (DIF.LT..010) GO TO 8
 7    CONTINUE
      WRITE (NPT,16)
      RETURN
 8    DIG(NN)=SYMB1(II)
      NN=NN+1
      N1=2
 9    L=1
C-----LOOP OVER ROWS IN MATRIX
      DO 11 M1=1,3
      FS1=ANTI*FS(M1,J,I)
      IF (FS1.EQ.0.) GO TO 10
      IF (FS1.EQ.1.) L=L-N1+2
      IF (FS1.EQ.-1.) L=L+2
      N1=N1+1
      DIG(NN)=SYMB2(L)
      NN=NN+1
 10   L=M1*3+1
 11   CONTINUE
      NN=NN-N1+3
 12   CONTINUE
      IF (ANTI.EQ.-1.) GO TO 13
      ANTI=-1.
      IF (ISYMCE.EQ.1) GO TO 6
 13   WRITE (NPT,17) (DIG(I1),I1=1,6),DIG(7),DIG(8),DIG(13),DIG(9),DIG(1
     10),DIG(13),DIG(11),DIG(12),(IP(I1),I1=1,12)
 14   CONTINUE
      RETURN
C
 15   FORMAT (/27H EQUIVALENT POINT POSITIONS/)
 16   FORMAT (33H EQUIPOINT CODE BADLY INTERPRETED)
 17   FORMAT (1X,2(2A3,1H,),2A3,5X,2(2A3,A1),2A3,2X,12A4)
      END
      BLOCK DATA                                                       
      CHARACTER*4 TABNC(128),TBXC(256)
      REAL M,NM
      INTEGER CT
      COMMON/TABCHR/TABNC,TBXC
      COMMON/TABLES/TBX(256,10),TBD(128,10),TABN(128)
      COMMON /ND/ NM/WAVEL/ M/BRAF/IB,CT /FLOR/ LPF,CV               
      DIMENSION NM(20),M(20),IB(8),CV(6),LPF(6),CT(8)                  
C-----LITERAL DATA FOR LAZY                                 
      DATA  NM(1)/1H1/, NM(2)/1H2/, NM(3)/1H3/, NM(4)/1H4/, NM(5)/1H5/,
     1NM(6)/1H6/,NM(7)/1HA/,NM(8)/1HB/,NM(9)/1HC/,NM(10)/1HD/,NM(11)/1HM
     2/,NM(12)/1HN/,NM(13)/1HP/,NM(14)/4HCU  /,NM(15)/1H//,NM(16)/1H-/,
     3NM(17)/1H /, NM(18)/2H  /,NM(19)/4H    /,NM(20)/2HSP/
      DATA LPF(1)/0/,LPF(2)/1/,LPF(3)/2/,LPF(4)/3/,LPF(5)/4/,LPF(6)/0/
      DATA CV(1)/2HDS/,CV(2)/2H 1/,CV(3)/2HNE/,CV(4)/2HGN/,CV(5)/2HGH/,C
     1V(6)/2H  /                                                        
      DATA IB(1)/1/,IB(2)/1/,IB(3)/2/,IB(4)/3/,IB(5)/4/,IB(6)/5/,IB(7)/6
     1/,IB(8)/7/                                                        
      DATA CT(1)/1H /,CT(2)/1HP/,CT(3)/1HI/,CT(4)/1HR/,CT(5)/1HF/,CT(6)/
     11HA/,CT(7)/1HB/,CT(8)/1HC/                                        
      DATA M(1)/4HCRA1/,M(2)/4HCRA2/,M(3)/4HCRB /,M(4)/4HCR  /,M(5)/4HFE
     1A1/,M(6)/4HFEA2/,M(7)/4HFEB /,M(8)/4HFE  /,M(9)/4HCUA1/,M(10)/4HCU
     2A2/,M(11)/4HCUB /,M(12)/4HCU  /,M(13)/4HMOA1/,M(14)/4HMOA2/,M(15)/
     34HMOB /,M(16)/4HMO  /,M(17)/4HAGA1/,M(18)/4HAGA2/,M(19)/4HAGB /,M(
     420)/4HAG  /                                                       
      END
C