.data
    t17: .space 16

.text
    addiu $sp, $zero, 0x10018000
    or $fp, $sp, $zero
    jal  main
    jal  programEnd

f1:
    lw $7, 0($fp)
    lw $8, 4($fp)
    lw $9, 8($fp)
    sub $fp,$fp,12
    add $10,$zero,0
    add $11,$8,$9
    sgt $12,$7,$11
    bgt $12,$zero,l1
    j l2
l1:
    mul $13,$8,$9
    add $14,$13,1
    add $15,$7,$14
    add $16,$zero,$15
    j l3
l2:
    add $16,$zero,$7
l3:
l6:
    add $a2,$zero,100
    sgt $17,$10,$a2
    xori $17,$17,1
    bgt $17,$zero,l4
    j l5
l4:
    add $a2,$zero,2
    mul $18,$16,$a2
    add $10,$zero,$18
    add $19,$16,1
    add $16,$zero,$19
    j l6
l5:
    add $v0,$zero,$10
    jr $ra

f2:
    lw $20, 0($fp)
    sub $fp,$fp,4
    add $21,$20,2
    add $20,$zero,$21
    add $a2,$zero,2
    mul $22,$20,$a2
    add $v0,$zero,$22
    jr $ra

main:
    add $a1,$zero,0
    add $a2,$zero,2
    mul $23,$a1,$a2
    add $23,$23,0
    add $24,$zero,3
    la $v1,t17
    mul $23,$23,4
    addu $23,$23,$v1
    sw $24,0($23)
    add $a1,$zero,0
    add $a2,$zero,2
    mul $25,$a1,$a2
    add $25,$25,0
    la $v1,t17
    mul $8,$8,4
    addu $8,$8,$v1
    lw $7,0($8)
    add $9,$7,1
    add $a1,$zero,0
    add $a2,$zero,2
    mul $10,$a1,$a2
    add $10,$10,1
    la $v1,t17
    mul $10,$10,4
    addu $10,$10,$v1
    sw $9,0($10)
    add $a1,$zero,0
    add $a2,$zero,2
    mul $11,$a1,$a2
    add $11,$11,0
    la $v1,t17
    mul $11,$11,4
    addu $11,$11,$v1
    lw $12,0($11)
    add $a1,$zero,0
    add $a2,$zero,2
    mul $13,$a1,$a2
    add $13,$13,1
    la $v1,t17
    mul $13,$13,4
    addu $13,$13,$v1
    lw $14,0($13)
    add $15,$12,$14
    add $a1,$zero,1
    add $a2,$zero,2
    mul $16,$a1,$a2
    add $16,$16,0
    la $v1,t17
    mul $16,$16,4
    addu $16,$16,$v1
    sw $15,0($16)
    sub $sp,$sp,4
    sw $ra, 0($sp)
    sub $sp,$sp,4
    sw $ra, 0($sp)
    add $a1,$zero,1
    add $a2,$zero,2
    mul $17,$a1,$a2
    add $17,$17,0
    la $v1,t17
    mul $17,$17,4
    addu $17,$17,$v1
    lw $18,0($17)
    add $fp,$fp,4
    sw $18, 0($fp)
    jal  f2
    lw $ra, 0($sp)
    add $sp,$sp,4
    add $19,$zero,$v0
    add $fp,$fp,12
    sw $20, 0($fp)
    sw $21, 4($fp)
    sw $19, 8($fp)
    jal  f1
    lw $ra, 0($sp)
    add $sp,$sp,4
    add $22,$zero,$v0
    add $a1,$zero,1
    add $a2,$zero,2
    mul $23,$a1,$a2
    add $23,$23,1
    la $v1,t17
    mul $23,$23,4
    addu $23,$23,$v1
    sw $22,0($23)
    jr $ra

programEnd:
    nop
